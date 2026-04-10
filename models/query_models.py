from pydantic import BaseModel

class QueryRequest(BaseModel):
    user_id: int
    query_text: str

class QueryResponse(BaseModel):
    query_id: int
    query_text: str
    response_text: str