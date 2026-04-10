from fastapi import APIRouter, HTTPException
from database.db_connection import get_connection
from models.query_models import QueryRequest, QueryResponse
from rag_project.retrieval import retrieve

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
    #for now we will just return the retrieved chunk texts as the response, but in a real implementation we would pass these to an LLM to generate a more natural response
    chunk_ids = result["chunk_ids"]
    chunk_texts = result["chunk_texts"]
    case_ids = list(set(result["case_ids"]))
    response_text = f"Retrieved {len(chunk_ids)} chunks from {len(case_ids)} cases."

    return QueryResponse(
        query_id=query_id,
        query_text=query_data.query_text,
        response_text=response_text
    )