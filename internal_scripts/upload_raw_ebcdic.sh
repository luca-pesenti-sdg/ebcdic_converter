find test-data/new/raw/EBCDIC/ ! -name H* -type f > tmp_list

while read -r file_path; do
    flux_name="$(echo $file_path | cut -d '/' -f5 | cut -d '.' -f1)"
    gcloud storage cp "$file_path" "gs://credem-hubble-pocedp-coll-apollo-landing/raw/EBCDIC/${flux_name}/"
done < tmp_list

