export PROJECT_ID="project-2c268745-0c2f-477a-b6a"
export USER_EMAIL="$(gcloud config get-value account)"
export BUCKET="insider-agent"
export PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')"

gcloud services enable \
  aiplatform.googleapis.com \
  storage.googleapis.com \
  --project "$PROJECT_ID"

for ROLE in \
  roles/aiplatform.user \
  roles/aiplatform.admin \
  roles/storage.admin \
  roles/serviceusage.serviceUsageConsumer \
  roles/iam.serviceAccountUser ; do
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="user:${USER_EMAIL}" \
    --role="$ROLE" \
    --condition=None
done

# Make sure the Vertex service agent exists
gcloud beta services identity create \
  --service=aiplatform.googleapis.com \
  --project="$PROJECT_ID"

VERTEX_SA="service-${PROJECT_NUMBER}@gcp-sa-aiplatform.iam.gserviceaccount.com"
REASONING_SA="service-${PROJECT_NUMBER}@gcp-sa-aiplatform-re.iam.gserviceaccount.com"

for SA in "$VERTEX_SA" "$REASONING_SA"; do
  gcloud storage buckets add-iam-policy-binding "gs://${BUCKET}" \
    --member="serviceAccount:${SA}" \
    --role="roles/storage.admin"
done

echo "sanity check: do you see these service accounts in the list"

gcloud auth application-default print-access-token >/dev/null && echo "ADC OK"
gcloud projects get-iam-policy "$PROJECT_ID" \
  --flatten="bindings[].members" \
  --filter="bindings.members:${USER_EMAIL}" \
  --format="value(bindings.role)"