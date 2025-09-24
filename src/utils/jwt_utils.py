import os
import jwt
import datetime
import logging
from typing import Optional, Dict, Any

logging.basicConfig(level=logging.INFO)
from typing import Optional, Dict, Any

# Read secret from environment variable (fallback to a dev default if missing)
SECRET_KEY = os.environ.get("INFOWAY_SECRET", "dev_secret_change_me")
ALGORITHM = "HS256"

def create_token(username: str, role: str, expires_hours: int = 1) -> str:
    """
    Create a JWT containing username and role with expiry in hours.
    """
    now = datetime.datetime.utcnow()
    payload = {
        "sub": username,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + datetime.timedelta(hours=expires_hours)).timestamp())
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify a JWT token and return its payload.
    Returns None if token is invalid or expired.
    """
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded
        logging.error("Token has expired.")
        return None
    except jwt.InvalidTokenError:
        logging.error("Invalid token.")
        return None
# Configure logging
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    # Create a tokensrc
    token = create_token("omkar", "admin", expires_hours=0.002)
    logging.info("Token: %s", token)

    # Verify the token
    payload = verify_token(token)
    if payload:
        logging.info("Valid token for user: %s with role: %s", payload["sub"], payload["role"])
    else:
        logging.info("Token invalid or expired")
   
else:
    logging.info("Token invalid or expired")