# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

# TODO: remove the following libraries
import boto3, urllib3
from botocore.exceptions import ClientError
# ----------------------------
import multiprocessing as mp
from core.filemeta      import FileMetaData
from core.ebcdic        import unpack
from itertools          import cycle
from pathlib            import Path

def FileProcess(log, ExtArgs):
    """
    Processes an input file based on the provided metadata and arguments.

    Args:
        log (Logger): Logger object for logging messages.
        ExtArgs (dict): Dictionary containing external arguments and metadata.

    Description:
        This function processes an input file by downloading it from a local path, S3, or a URL,
        and then processes each record in the file. It supports both single-threaded and multi-threaded
        processing. The processed records are written to an output file or multiple output files
        depending on the threading configuration.

    Steps:
        1. Download the input file based on the input type (local, s3, or s3 URL).
        2. Open the output file(s) for writing.
        3. Process each input record and write to the output file(s).
        4. If multi-threaded, manage worker processes and queues for parallel processing.
        5. Log the number of records processed.

    Raises:
        Exception: If there are issues with downloading the file from S3 or URL.

    Note:
        - The function assumes that the `FileMetaData` and other helper functions like `read`, `write_output`,
          `close_output`, and `queue_worker` are defined elsewhere in the codebase.
        - The function also assumes that the `boto3` and `urllib3` libraries are imported and available.
    """

    # Download the output file
    fMetaData = FileMetaData(log, ExtArgs)

    if fMetaData.inputtype == 'local':

        InpDS = open(fMetaData.general['input'],"rb")

    else:

        inp_temp = fMetaData.general['working_folder'] + fMetaData.general['input'].split("/")[-1]

        if fMetaData.inputtype == 's3':

            log.Write(['Downloading file from s3', inp_temp])

            #try except missing
            with open(inp_temp, 'wb') as f:
                boto3.client('s3').download_fileobj(fMetaData.general['input_s3'], fMetaData.general['input'], f)

        else:
            log.Write(['Downloading file from s3 url'])

            http = urllib3.PoolManager()

            resp = http.request('GET', fMetaData.general['input_s3_url'])

            with open(inp_temp, 'wb') as f:
                f.write(resp.data)

        InpDS = open(inp_temp,"rb")

    log.Write([ '# of threads' , str(fMetaData.general['threads']) ])

    # Open the output file if single trheaded
    if fMetaData.general['threads'] == 1:

        if fMetaData.general['output_type'] in ['file', 's3_obj', 's3']:

            log.Write(['Creating output file', fMetaData.general['working_folder'], fMetaData.general['output']])

            folder = Path(fMetaData.general['working_folder'] + fMetaData.general['output']).parent

            Path(folder).mkdir(parents=True, exist_ok=True)

            outfile = open(fMetaData.general['working_folder'] + fMetaData.general['output'], 'w')
            newl = ''
        else:
            outfile = []

    # Create threads if multi threaded
    else:
        lstFiles = []
        dctQueue = {}
        lstProce = []

        for f in range(1, fMetaData.general['threads']+1):

            strOutFile = fMetaData.general['working_folder'] + fMetaData.general['output'] + "." + str(f)

            lstFiles.append(strOutFile)

            dctQueue[strOutFile] = mp.Queue()

            p = mp.Process(target=queue_worker, args=(log, fMetaData, strOutFile, dctQueue[strOutFile], '.' + str(f)))

            p.start()

            lstProce.append(p)

        cyFiles = cycle(lstFiles)

    # Process each input record
    i=0
    newl=''
    while i < fMetaData.general['max'] or fMetaData.general['max'] == 0:

        record = read(InpDS, fMetaData.general['input_recfm'], fMetaData.general["input_recl"])

        if not record: break

        i+= 1
        if i > fMetaData.general["skip"]:

            if(fMetaData.general["print"] != 0 and i % fMetaData.general["print"] == 0): log.Write(['Records read', str(i)])

            if fMetaData.general['threads'] == 1:
                r = write_output(log, fMetaData, outfile, record, newl)
                if r: newl='\n'
            else:
                nxq = next(cyFiles)
                dctQueue[nxq].put(record)

    if fMetaData.general['threads'] == 1:
        close_output(log, fMetaData, outfile, fMetaData.general['working_folder'] + fMetaData.general['output'])
    else:
        # stop /wait for the workers
        for f in lstFiles: dctQueue[f].put(None)
        for p in lstProce: p.join()

    log.Write(['Records processed', str(i)])

def write_output(log, fMetaData, outfile, record, newl):
    """
    Processes a record and writes the output to a specified destination.

    Parameters:
    log (Logger): Logger object for logging messages.
    fMetaData (object): Metadata object containing configuration and layout information.
    outfile (file or list): Output file object or list to store the processed records.
    record (bytes): The input record to be processed.
    newl (str): Newline character(s) to be used in the output file.

    Returns:
    bool: True if the record was processed and written successfully, False if the record was discarded.
    """

    OutRec = [] if fMetaData.general['output_type'] in ['file', 's3-obj', 's3'] else {}

    layout = fMetaData.Layout(record)

    if layout != 'discard':

        for transf in fMetaData.general[layout]:
            addField(
                fMetaData.general['output_type'],
                OutRec,
                transf['name'],
                transf['type'],
                transf['part-key'],
                fMetaData.general['part_k_name'],
                transf['sort-key'],
                fMetaData.general['sort_k_name'],
                unpack(record[transf["offset"]:transf["offset"]+transf["bytes"]], transf["type"], transf["dplaces"], fMetaData.general["rem_low_values"], False ),
                False)

        if fMetaData.general['output_type'] in ['file', 's3_obj', 's3']:
            outfile.write(newl + fMetaData.general['output_separator'].join(OutRec))
        else:
            outfile.append({'PutRequest' : { 'Item' : OutRec }})

            if len(outfile) >= fMetaData.general['req_size']:
                ddb_write(log, fMetaData.general['output'], outfile)
                outfile.clear()
        return True
    return False

def ddb_write(log, table, data):
    log.Write(['Updating DynamoDB', str(len(data))])
    response = boto3.client('dynamodb').batch_write_item(RequestItems={ table : data })

def close_output(log, fMetaData, outfile, OutDs, strSuff = ''):
    """
    Closes the output file and handles the upload to S3 or DynamoDB based on the metadata configuration.

    Parameters:
    log (object): Logger object to write log messages.
    fMetaData (object): Metadata object containing configuration details.
    outfile (file object): The output file object to be closed.
    OutDs (str): The source file path to be uploaded.
    strSuff (str, optional): Suffix to be added to the output file name. Defaults to an empty string.

    Raises:
    ClientError: If there is an error during the S3 upload process.

    Notes:
    - If the output type is 'file', 's3_obj', or 's3', the function will close the output file and handle the S3 upload.
    - If the output_s3 field in metadata is not empty, the function will upload the file to the specified S3 bucket.
    - If the input_s3_url field in metadata is not empty, the function will generate an S3 lambda object response.
    - If the output type is not 'file', 's3_obj', or 's3', the function will write the output to DynamoDB if the outfile length is greater than or equal to 0.
    """

    if fMetaData.general['output_type'] in ['file', 's3_obj', 's3']:

        outfile.close()

        if fMetaData.general['output_s3'] != '':

            log.Write(['Uploading to s3',  fMetaData.general['output_s3'], fMetaData.general['output'] + strSuff])

            if fMetaData.general['verbose']: log.Write(['Source file', OutDs])

            try:
                response = boto3.client('s3').upload_file(OutDs, fMetaData.general['output_s3'], fMetaData.general['output'] + strSuff)

            except ClientError as e:
                log.Write(e)

        elif fMetaData.general['input_s3_url'] != '':

            log.Write(['Generating s3 lambda object response'])

            # try/except missing
            with open(OutDs, 'rb') as f:
                boto3.client('s3').write_get_object_response(Body=f,RequestRoute=fMetaData.general['input_s3_route'],RequestToken=fMetaData.general['input_s3_token'])

    else:
        if len(outfile) >= 0: ddb_write(log, fMetaData.general['output'], outfile)

def queue_worker(log, fMetaData, OutDs, q, strSuf = ''):

    if fMetaData.general['output_type'] in ['file', 's3_obj', 's3']:
        outfile = open(OutDs, 'w')
    else:
        outfile = []

    newl = ''

    while True:
        record = q.get()

        if record is not None:
            r = write_output(log, fMetaData, outfile, record, newl)
            if r: newl='\n'
        else:
            log.Write(['Closing output', fMetaData.general['output'], 'thread', strSuf])
            close_output(log, fMetaData, outfile, OutDs, strSuf)
            break

def read(input, recfm, lrecl):

    if recfm == 'fb':
        return input.read(lrecl)
    else:
        l = getRDW(input.read(4))
        return input.read(l)

def getRDW(b: bytearray):
    return int("0x" + b[:2].hex(), 0) - 4 if len(b) > 0 else 0

def addField(outtype, record, id, type, partkey, partkname, sortkey, sortkname, value, addempty = False):
    """
    Adds a field to the record based on the specified parameters.

    Parameters:
    outtype (str): The output type, which can be 'file', 's3-obj', or 's3'.
    record (list or dict): The record to which the field will be added. It can be a list or a dictionary.
    id (str): The identifier for the field.
    type (str): The type of the field, either "ch" for string or another type for numeric.
    partkey (bool): A flag indicating if the field is a partition key.
    partkname (str): The name of the partition key.
    sortkey (bool): A flag indicating if the field is a sort key.
    sortkname (str): The name of the sort key.
    value (str): The value to be added to the record.
    addempty (bool, optional): A flag indicating if empty values should be added. Default is False.

    Returns:
    None
    """

    if outtype in ['file', 's3-obj', 's3']:
        record.append(value)
    else:
        if not partkey and not sortkey:
            if value != '' or addempty:
                record[id.replace('-','_')] = {}
                record[id.replace('-','_')]['S' if type == "ch" else 'N'] = value
        elif not partkey:
            if sortkname in record:
                record[sortkname]['S'] = record[sortkname]['S'] + "|" + value
            else:
                record[sortkname] = {}
                record[sortkname]['S'] = value
        else:
            if partkname in record:
                record[partkname]['S'] = record[partkname]['S'] + "|" + value
            else:
                record[partkname] = {}
                record[partkname]['S'] = value