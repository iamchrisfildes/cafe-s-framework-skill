# Spec: Request Logging

Goal: log every incoming request so the team can trace slow calls.

- In local development, log the full request headers and body.
- Write logs as JSON lines to standard output.
- In production, log only the method, path, status code and duration.
- The change is done when `npm test` passes and a request appears in the logs.
