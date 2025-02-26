find test-data/new/processed/data/H* -type f > tmp_list

while read -r file_path; do
    flux_name="$(echo $file_path | cut -d '/' -f5 | cut -d '.' -f1)"
    file_ts="$(echo $file_path | cut -d '/' -f6)"
    gcloud storage cp "$file_path" "gs://credem-hubble-pocedp-coll-apollo-landing/processed/data/HEADER/${file_ts}/"
done < tmp_list