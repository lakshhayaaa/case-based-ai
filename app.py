from fastapi import FastAPI
from routes.auth import router as auth_router
from routes.query import router as query_router
from fastapi.middleware.cors import CORSMiddleware

app=FastAPI(title="Case-Based AI API", description="API for managing entrepreneurial cases, user queries, and AI responses.")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
app.include_router(auth_router)
app.include_router(query_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Case-Based AI API is running!"}