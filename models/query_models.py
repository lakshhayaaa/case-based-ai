from pydantic import BaseModel

class QueryRequest(BaseModel):
    query_text: str

class QueryResponse(BaseModel):
    query_id: int
    query_text: str
    response_text: str
    trust_score: float
    supported_claims: int
    total_claims: int