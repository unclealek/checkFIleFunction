## GCS File Size Checker (Cloud Function)

This Google Cloud Function is triggered by Google Cloud Storage (GCS) events. It checks the size of newly created/updated objects and, if a file exceeds 2 MB, moves it to a destination bucket under the `large_files/` prefix.

### How it works
- Trigger: GCS (Object finalize or metadata update)
- Logic: Reads the uploaded file size; if size > 2 MB, copies it to the destination bucket `2mb-bucket/large_files/<filename>` and deletes the original.
- Entry point: `check_file_size_and_move` in `function.py`

### Files
- `function.py`: Cloud Function implementation
- `requirements.txt`: Python dependencies (uses `google-cloud-storage`)

### Prerequisites
- Google Cloud Project with billing enabled
- `gcloud` CLI authenticated and configured
- A source GCS bucket (the one that triggers the function)
- A destination GCS bucket named `2mb-bucket` (or change the constant below)

### Configuration
Update the destination bucket name in `function.py` if needed:

```python
INVALID_FILES_BUCKET = "2mb-bucket"
```

### Required IAM Permissions
The Cloud Function's service account needs access to:
- Source bucket: read/list objects (e.g., `roles/storage.objectViewer`)
- Destination bucket: write objects and delete if needed (e.g., `roles/storage.objectAdmin` on the destination bucket only)

Least-privilege tip: grant `roles/storage.objectCreator` and `roles/storage.objectViewer` as appropriate instead of broader roles if your workflow allows.

### Deploy
Replace placeholders with your values.

```bash
# Variables
PROJECT_ID="your-gcp-project-id"
REGION="us-central1"             # or your preferred region
SOURCE_BUCKET="your-source-bucket"
FUNCTION_NAME="gcs-file-size-checker"

gcloud functions deploy "$FUNCTION_NAME" \
  --project="$PROJECT_ID" \
  --region="$REGION" \
  --runtime=python310 \
  --trigger-resource="$SOURCE_BUCKET" \
  --trigger-event=google.storage.object.finalize \
  --entry-point=check_file_size_and_move \
  --source=. \
  --timeout=60s
```

Notes:
- Runtime can be `python39`, `python310`, or `python311` depending on availability.
- Ensure `requirements.txt` is in the root so dependencies are installed.

### Test
1. Upload a small file (< 2 MB) to the source bucket and confirm logs show it is within the limit.
2. Upload a large file (> 2 MB) to the source bucket and confirm it is moved to `gs://2mb-bucket/large_files/` (or your configured bucket).

### Logs
View logs after testing:

```bash
gcloud functions logs read "$FUNCTION_NAME" --region="$REGION" --project="$PROJECT_ID" --limit=100
```

### Troubleshooting
- If the function cannot write to the destination bucket, verify the service account permissions.
- If file size prints as `None`, ensure the event is an object finalize/update event and that the blob is reloaded (already handled in code).
- Confirm the destination bucket exists and the constant `INVALID_FILES_BUCKET` matches it.


# checkFIleFunction
