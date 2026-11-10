# Runbook: Nightly Backup Failed

Use this when the `nightly-backup` job fails.

1. Open the job's latest run log: `kubectl logs job/nightly-backup -n data`.
2. If the log ends with `disk full`, run `kubectl apply -f ops/backup-pvc-50gi.yaml`, then rerun the job with `kubectl create job --from=cronjob/nightly-backup nightly-backup-retry -n data`.
3. For any other error, post the last 20 log lines in the `#data-oncall` channel and stop.

You are done when the retry job shows `Completed` in `kubectl get jobs -n data`.
