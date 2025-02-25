find test-data/new/raw/EBCDIC/H* -type f > tmp_list

while read -r file_path; do
    flux_name="$(echo $file_path | cut -d '/' -f5 | cut -d '.' -f1)"
    gcloud storage cp "$file_path" "gs://credem-hubble-pocedp-coll-apollo-landing/raw/EBCDIC/HEADER/${flux_name}/${file_ts}/"
done < tmp_list