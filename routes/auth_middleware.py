from fastapi import Header, HTTPException
from database.db_connection import get_connection
import hashlib
from datetime import datetime, timezone

def get_current_user(authorization: str = Header(...)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")
    token = authorization.split(" ")[1]
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
                SELECT user_id, expires_at
                FROM user_sessions
                WHERE token_hash = %s
                """, (token_hash,))
    
    session = cur.fetchone()
    cur.close()
    conn.close()

    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user_id, expires_at = session
    if expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Token has expired")

    return user_id