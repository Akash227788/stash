#!/bin/bash
# Commands to create secrets in Secret Manager

echo "AIzaSyCF6j9dnNaKmZ1w4ZmNt79epRTSMVNHA6Y" | gcloud secrets create genai-api-key --data-file=- --project=stash-467107 2>/dev/null || echo "AIzaSyCF6j9dnNaKmZ1w4ZmNt79epRTSMVNHA6Y" | gcloud secrets versions add genai-api-key --data-file=- --project=stash-467107
echo "AqwHL33GNqmqoSlcYwVJRdRXHO5jFGJjT6fJTrHJTN0hh-qbTSY1ayVuvVIjqHPpkLQ1fqYeXPFUnvjtwvYQ1g" | gcloud secrets create stash-secret-key --data-file=- --project=stash-467107 2>/dev/null || echo "AqwHL33GNqmqoSlcYwVJRdRXHO5jFGJjT6fJTrHJTN0hh-qbTSY1ayVuvVIjqHPpkLQ1fqYeXPFUnvjtwvYQ1g" | gcloud secrets versions add stash-secret-key --data-file=- --project=stash-467107
echo "your-jwt-secret-key" | gcloud secrets create jwt-secret-key --data-file=- --project=stash-467107 2>/dev/null || echo "your-jwt-secret-key" | gcloud secrets versions add jwt-secret-key --data-file=- --project=stash-467107
echo "" | gcloud secrets create redis-password --data-file=- --project=stash-467107 2>/dev/null || echo "" | gcloud secrets versions add redis-password --data-file=- --project=stash-467107
echo "7yLwXeQF0V60vUhseuR2199DUTQ_IGHWhle-cmAOL3Y" | gcloud secrets create webhook-secret --data-file=- --project=stash-467107 2>/dev/null || echo "7yLwXeQF0V60vUhseuR2199DUTQ_IGHWhle-cmAOL3Y" | gcloud secrets versions add webhook-secret --data-file=- --project=stash-467107
echo "" | gcloud secrets create smtp-password --data-file=- --project=stash-467107 2>/dev/null || echo "" | gcloud secrets versions add smtp-password --data-file=- --project=stash-467107
