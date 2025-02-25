
for file_path in test-data/new/raw/EBCDIC/*; do
    file_name=$(basename "$file_path")
    file_base="${file_name%%.*}"
    file_ts="${file_name#*.}"
    file_ts_formatted="${file_ts:0:4}-${file_ts:4:2}-${file_ts:6:2}T${file_ts:8:2}:${file_ts:10:2}:${file_ts:12:2}"
    python3 src/main.py both test-data/new/raw/copybook/header.txt test-data/new/processed/copybook_json/header.json -input "$file_path" -output test-data/new/processed/data/${file_base}/LOAD_TS=${file_ts_formatted}/${file_base}.parquet -print 10000 -verbose true
done