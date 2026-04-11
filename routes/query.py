from fastapi import APIRouter, HTTPException
from database.db_connection import get_connection
from models.query_models import QueryRequest, QueryResponse
from rag_project.retrieval import retrieve
from rag_project.llm_generator import generate_answer
from rag_project.verification import verify_response, calculate_trust_score, save_verification

router = APIRouter()

@router.post("/ask", response_model=QueryResponse)
def ask_query(query_data: QueryRequest):
    conn = get_connection()
    curr = conn.cursor()

    # verify user exists
    curr.execute("SELECT user_id FROM users WHERE user_id=%s", (query_data.user_id,))
    if not curr.fetchone():
        raise HTTPException(status_code=404, detail="User not found")

    # store the user query in the database
    curr.execute(
        "INSERT INTO user_queries (user_id, query_text) VALUES (%s, %s) RETURNING query_id",
        (query_data.user_id, query_data.query_text)
    )
    query_id = curr.fetchone()[0]
    conn.commit()
    curr.close()
    conn.close()

    result = retrieve(query_id=query_id, query=query_data.query_text)

    chunk_ids = result["chunk_ids"]
    chunk_texts = result["chunk_texts"]
    case_ids = list(set(result["case_ids"]))

    answer = generate_answer(query_data.query_text, chunk_texts)
    conn = get_connection()
    curr = conn.cursor()

    # 5️⃣ Store AI response
    curr.execute(
        """
        INSERT INTO ai_responses (query_id, final_response_text)
        VALUES (%s, %s)
        RETURNING response_id
        """,
        (query_id, answer)
    )

    response_id = curr.fetchone()[0]

    # 6️⃣ Store chunk mappings
    for chunk_id in chunk_ids:
        curr.execute(
            """
            INSERT INTO response_chunk_mapping (response_id, chunk_id, used_for)
            VALUES (%s, %s, %s)
            """,
            (response_id, chunk_id, "retrieval")
        )

    # 7️⃣ Store case mappings
    for case_id in case_ids:
        curr.execute(
            """
            INSERT INTO response_case_mapping (response_id, case_id)
            VALUES (%s, %s)
            """,
            (response_id, case_id)
        )

    conn.commit()
    curr.close()
    conn.close()

    # 🔎 Verify response
    verification_results = verify_response(answer, chunk_texts, chunk_ids)

    #Calculate trust score
    trust_score_data = calculate_trust_score(verification_results)

    # Save verification + trust score
    save_verification(response_id, verification_results, trust_score_data)

    trust_score, supported, total = trust_score_data

    return QueryResponse(
        query_id=query_id,
        query_text=query_data.query_text,
        response_text=f"{answer}\n\nTrust Score: {trust_score:.2f}% ({supported}/{total} claims supported)"
        )