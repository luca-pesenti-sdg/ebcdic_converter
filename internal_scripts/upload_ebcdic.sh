find test-data/new/processed/data/ ! -name H* -type f > tmp_list

while read -r file_path; do
    filename="$(echo $file_path | cut -d '/' -f7)"
    flux_name="$(echo $file_path | cut -d '/' -f5)"
    file_ts="$(echo $file_path | cut -d '/' -f6)"
    gcloud storage cp "$file_path" "gs://credem-hubble-pocedp-coll-apollo-landing/processed/data/${flux_name}/${file_ts}/"
done < tmp_list