
from sentence_transformers import SentenceTransformer
import numpy as np
from database.db_connection import get_connection

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')


#  Step 1: Extract claims (split sentences)
def extract_claims(response_text):
    claims = [sentence.strip() for sentence in response_text.split('.') if sentence.strip()]
    return claims


#  Step 2: Cosine similarity
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


#  Step 3: Verify each claim
def verify_response(response_text, chunk_texts, chunk_ids):
    claims = extract_claims(response_text)

    verification_results = []

    for claim in claims:
        claim_embedding = model.encode(claim)

        best_score = 0
        best_chunk_id = None

        for chunk_id, chunk in zip(chunk_ids, chunk_texts):
            chunk_embedding = model.encode(chunk)

            score = cosine_similarity(claim_embedding, chunk_embedding)

            if score > best_score:
                best_score = score
                best_chunk_id = chunk_id

        # Threshold (can tune later)
        status = "verified" if best_score > 0.6 else "not_verified"

        verification_results.append({
            "claim": claim,
            "chunk_id": best_chunk_id,
            "score": float(best_score),
            "status": status
        })

    return verification_results


#  Step 4: Calculate trust score
def calculate_trust_score(verification_results):
    total = len(verification_results)
    supported = sum(1 for v in verification_results if v["status"] == "verified")

    if total == 0:
        return 0, 0, 0

    trust_score = (supported / total) * 100

    return trust_score, supported, total


#  Step 5: Save verification + trust score
def save_verification(response_id, verification_results, trust_score_data):
    conn = get_connection()
    cur = conn.cursor()

    # Insert verification logs
    for v in verification_results:
        cur.execute("""
            INSERT INTO verification_log (response_id, claim_text, chunk_id, similarity_score, status)
            VALUES (%s, %s, %s, %s, %s)
        """, (response_id, v["claim"], v["chunk_id"], v["score"], v["status"]))

    # Insert trust score
    trust_score, supported, total = trust_score_data

    cur.execute("""
        INSERT INTO trust_score (response_id, trust_score, supported_claim, total_claims)
        VALUES (%s, %s, %s, %s)
    """, (response_id, trust_score, supported, total))

    conn.commit()
    cur.close()
    conn.close()