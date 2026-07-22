"""
Simple API key authentication for CourtGuard.

This is intentionally simple (a single shared key) which is a reasonable,
defensible choice for a final-year project prototype. In your report you can
note that a production legal system would need proper per-user authentication
(e.g. OAuth2, JWT tokens tied to individual lawyer/investigator accounts) as
future work — but a single API key is enough to stop random public users from
hitting your hosted API for free once it's deployed.
"""
import os
from fastapi import Header, HTTPException

# The key itself is read from an environment variable, NOT hardcoded here.
# This means the real key never gets committed to GitHub.
API_KEY = os.environ.get("COURTGUARD_API_KEY", "dev-local-key-change-me")


def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return True