from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.database import Base, engine
from routers import files, users, transcribe, export

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Meeting Summarizer & Action Tracker",
    description="Records, transcribes, summarizes meetings and extracts tasks.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(users.router)
app.include_router(files.router)
app.include_router(transcribe.router)
app.include_router(export.router)

@app.get("/check")
def root():
    return {"message": "API is running"}
