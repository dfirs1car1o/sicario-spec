# Abuse Cases — Customer Invoice Export API

- A standard user requests an invoice id belonging to another organization
  (expected: 403, logged as a denial).
- An anonymous client calls the endpoint directly (expected: 401).
- A caller enumerates sequential ids to discover accessible invoices (expected:
  denials indistinguishable from not-found; rate-limited at the gateway).
- A caller submits a malformed or oversized id to provoke an unhandled error
  (expected: 400 with no internal detail leaked).
