
for file_path in test-data/new/processed/copybook_json/*.json; do
    file_name=$(basename "$file_path")
    file_base="${file_name%%.*}"
    gcloud storage cp "$file_path" "gs://credem-hubble-pocedp-coll-apollo-landing/processed/copybook_json/${file_base}/"
done

# gcloud storage cp test-data/json/CLANAGRU.2024121200000000.json 