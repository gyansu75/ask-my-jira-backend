from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from core.normalizer import normalize_jira_data
from core.ai_parser import process_jira_query

app = FastAPI(
    title="Codegeist Context Copilot API",
    description="AI backend for Atlassian Forge Jira integration",
)

# Allow CORS for Forge requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AIQueryPayload(BaseModel):
  prompt: str
  raw_issues: list


@app.post("/api/analyze-jira")
def analyze_jira(payload: AIQueryPayload):
  try:
    normalized_issues = normalize_jira_data(payload.raw_issues)
    result = process_jira_query(payload.prompt, normalized_issues)
    return {"status": "success", "result": result}
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def health_check():
  return {"status": "online", "message": "Codegeist FastAPI backend is running!"}