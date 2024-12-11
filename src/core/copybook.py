# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

# FUNCTIONS TO HANDLE THE HIERARCHICAL STACK #
def fGetSetack():
    global stack, output
    tmp = output
    for k in stack:
        tmp = tmp[stack[k]]
    return tmp

def fRemStack(iStack,iLevel):
    NewStack = {}
    for k in iStack:
        if k < iLevel: NewStack[k] = iStack[k]
    return NewStack

#PIC 999, 9(3), XXX, X(3)...
def getPicSize(arg):
    if arg.find("(") > 0: 
        return int(arg[arg.find("(")+1:arg.find(")")])
    else:
        return len(arg)

# TYPE AND LENGTH CALCULATION #
def getLenType(atr, p):
    ret = {}
    #FirstCh = atr[3][:1].upper()
    #Picture = atr[3].upper()
    FirstCh = atr[p][:1].upper()
    Picture = atr[p].upper()

    #data type
    if   'COMP-3'in atr and FirstCh=='S': ret['type'] = "pd+"
    elif 'COMP-3'in atr:                  ret['type'] = "pd"
    elif 'COMP'  in atr and FirstCh=='S': ret['type'] = "bi+"
    elif 'COMP'  in atr:                  ret['type'] = "bi"
    elif FirstCh=='S':                    ret['type'] = "zd+"
    elif FirstCh=='9':                    ret['type'] = "zd"
    else:                                 ret['type'] = "ch"

    #Total data length
    PicNum = Picture.replace("V"," ").replace("S","").replace("-","").split()
    
    Lgt = getPicSize(PicNum[0])

    if len(PicNum) == 1 and FirstCh !='V':
        ret['dplaces'] = 0
    elif FirstCh !='V':
        ret['dplaces'] = getPicSize(PicNum[1])
        Lgt += ret['dplaces']
    else:
        ret['dplaces'] = getPicSize(PicNum[0])

    ret['length'] = Lgt

    #Data size in bytes
    if   ret['type'][:2] == "pd": ret['bytes'] = int(Lgt/2)+1
    elif ret['type'][:2] == "bi": 
        if   Lgt <  5:             ret['bytes'] = 2
        elif Lgt < 10:             ret['bytes'] = 4
        else         :             ret['bytes'] = 8
    else:                          
        if FirstCh=='-': Lgt += 1
        ret['bytes'] = Lgt
        
    return ret

############# DICTIONARY AND HIERARCHICAL LOGIC ###########################
def add2dict(lvl, grp, itm, stt, id):
    """
    Adds an item to a dictionary with specific attributes and handles nested structures.
    Parameters:
    lvl (int): The level of the item in the hierarchy.
    grp (bool): Indicates if the item is a group.
    itm (str): The name of the item.
    stt (list): A list of strings representing the item's attributes.
    id (int): The identifier for the item.
    Raises:
    Exception: If 'OCCURS' is present in stt without 'TIMES'.
    Notes:
    - If the item name is "FILLER", it appends a unique number to it.
    - Manages a stack to handle nested structures based on the level.
    - Extracts and sets various attributes for the item, such as 'occurs', 'redefines', 'pict', 'type', 'length', 'bytes', and 'dplaces'.
    """

    global cur, output, last, stack, FillerCount

    if itm.upper() == "FILLER":
        FillerCount += 1
        itm = itm + "_" + str(FillerCount)

    if lvl <= cur: stack = fRemStack(stack, lvl)

    stk = fGetSetack()
    stk[itm]= {}
    stk[itm]['id'] = id
    stk[itm]['level'] = lvl
    stk[itm]['group'] = grp
    
    if 'OCCURS'   in stt: 
        if 'TIMES' in stt:
            stk[itm]['occurs'] = int(stt[stt.index('TIMES')-1])
        else:
            raise Exception('OCCURS WITHOU TIMES?' + ' '.join(stt))

    if 'REDEFINES'in stt: stk[itm]['redefines'] = stt[stt.index('REDEFINES')+1]

    if grp == True:
        stack[lvl] = itm
        cur = lvl
    else:
        tplen = {}
        pic = stt.index('PIC')+1
        tplen = getLenType(stt, pic)
        #stk[itm]['pict'] = stt[3]
        stk[itm]['pict'] = stt[pic]
        stk[itm]['type'] = tplen['type']
        stk[itm]['length'] = tplen['length']
        stk[itm]['bytes'] = tplen['bytes']
        stk[itm]['dplaces'] = tplen['dplaces']

############################### MAIN ###################################
# READS, CLEANS AND JOINS LINES #

FillerCount=0
cur=0
output={}
stack = {}

def toDict(lines):
    """
    Converts a list of lines from a copybook into a dictionary representation.
    Args:
        lines (list of str): The lines from the copybook file.
    Returns:
        dict: A dictionary representation of the copybook fields.
    Raises:
        SystemExit: If an unexpected character is found in column 7 of any line.
    Notes:
        - Lines with a '*' in column 7 are considered comments and ignored.
        - Lines with 'SKIP1', 'SKIP2', or 'SKIP3' in the first attribute are skipped.
        - Fields are split by periods and attributes are further split by spaces.
        - The function assumes that the `add2dict` function is defined elsewhere in the code.
    """

    id = 0
    stt = ""
    for line in lines: 
        if len(line[6:72].strip()) > 1:
            if line[6] in [' ' , '-']: 
                if not line[6:72].split()[0] in ['SKIP1','SKIP2','SKIP3']:
                    stt += line[6:72].replace('\t', ' ')
            elif line[6] != '*':
                print('Unnexpected character in column 7:', line) 
                quit()

    # READS FIELD BY FIELD / SPLITS ATTRIBUTES #
    for variable in stt.split("."):
        
        attribute=variable.split()

        if len(attribute) > 0:
            if attribute[0] != '88': 
                id += 1
                add2dict(int(attribute[0]), False if 'PIC'in attribute else True, attribute[1], attribute, id)

    return output