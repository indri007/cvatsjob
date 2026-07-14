gcloud run deploy jobsync-chatbot \
  --source . \
  --region asia-southeast2 \
  --allow-unauthenticated \
  --memory 1Gi \
  --set-env-vars EMBEDDING_PROVIDER=gemini \
  --set-secrets GOOGLE_API_KEY=GEMINI_API_KEY:latest,OPENAI_API_KEY=OPENAI_API_KEY:latest
