from fastapi import APIRouter, HTTPException
from database.db_connection import get_connection
from models.auth_models import SignUpRequest, SignInRequest, UserResponse
import bcrypt
import secrets
import hashlib
from datetime import datetime, timedelta, timezone

router = APIRouter()

@router.post("/signup", response_model=UserResponse)
def signup(data: SignUpRequest):
    conn = get_connection()
    cur = conn.cursor()

    # Check if email already exists
    cur.execute("SELECT user_id FROM users WHERE email = %s", (data.email,))
    if cur.fetchone():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Insert into users table
    cur.execute(
        "INSERT INTO users (name, email) VALUES (%s, %s) RETURNING user_id, name, email",
        (data.name, data.email)
    )
    user = cur.fetchone()

    # Hash password and insert into user_auth
    password_hash = bcrypt.hashpw(data.password.encode(), bcrypt.gensalt()).decode()
    cur.execute(
        "INSERT INTO user_auth (user_id,password_hash) VALUES (%s,%s)",
        (user[0], password_hash)
    )

    conn.commit()
    cur.close()
    conn.close()

    return {"user_id": user[0], "name": user[1], "email": user[2]}


@router.post("/signin", response_model=UserResponse)
def signin(data: SignInRequest):
    conn = get_connection()
    cur = conn.cursor()

    # Get user + password hash in one join
    cur.execute("""
        SELECT u.user_id, u.name, u.email, ua.password_hash
        FROM users u
        JOIN user_auth ua ON u.user_id = ua.user_id
        WHERE u.email = %s
    """, (data.email,))
    
    user = cur.fetchone()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    print("Hashed password from DB:", user[3])  # Debugging line to check the stored hash
    stored_hash = user[3]  # Ensure the stored hash is bytes
    if isinstance(stored_hash, memoryview):
        stored_hash = bytes(stored_hash).decode('utf-8')
    elif isinstance(stored_hash, bytes):
        stored_hash = stored_hash.decode('utf-8')
    # Verify password
    if not bcrypt.checkpw(data.password.encode(), stored_hash.encode()):
        raise HTTPException(status_code=401, detail="Incorrect password")
    
    token=secrets.token_hex(32) # Generate a random token (for demonstration)
    print("Generated token:", token)  # Debugging line to check the generated token
    token_hash = hashlib.sha256(token.encode()).hexdigest()  # Hash the token before storing
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)  # Token valid for 7 days
    #store the token hash in the database
    cur.execute("""
                INSERT INTO user_sessions (user_id, token_hash, expires_at)
                VALUES (%s, %s, %s)
                """, (user[0], token_hash, expires_at))
    conn.commit()
    cur.close()
    conn.close()

    return {"user_id": user[0], "name": user[1], "email": user[2],"token": token}