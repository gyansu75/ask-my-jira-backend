import json
import os
import pandas as pd
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def process_jira_query(query: str, issues: list) -> dict:
  """Uses Groq to analyze Jira issue context and filter records."""
  df = pd.DataFrame(issues)

  system_prompt = """
    You are Codegeist Context Copilot, an AI engineering assistant.
    Analyze the user's natural language query against the provided Jira issue records.
    Return a valid JSON object with EXACTLY these three keys:
    1. "filter_status": string (Match status name like "Done", "In Progress", "To Do", or "All")
    2. "filter_priority": string (Match priority like "High", "Medium", "Low", or "All")
    3. "message": string (A concise, professional technical summary answering the user's question)
    
    Do not include markdown blocks like ```json, just return raw JSON.
    """

  user_prompt = f"User Query: '{query}'\nJira Issues Summary: {df.to_dict(orient='records')}"

  try:
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        model="openai/gpt-oss-20b",
        temperature=0.1,
        response_format={"type": "json_object"},
    )

    parsed = json.loads(chat_completion.choices[0].message.content)
    f_status = parsed.get("filter_status", "All")
    f_prio = parsed.get("filter_priority", "All")
    msg = parsed.get(
        "message", "Here are the Jira issues matching your query:"
    )

    filtered_df = df.copy()
    if f_status != "All" and not filtered_df.empty:
      filtered_df = filtered_df[
          filtered_df["status"].str.lower() == f_status.lower()
      ]
    if f_prio != "All" and not filtered_df.empty:
      filtered_df = filtered_df[
          filtered_df["priority"].str.lower() == f_prio.lower()
      ]

    return {"message": msg, "data": filtered_df.to_dict(orient="records")}

  except Exception as e:
    print(f"Groq AI Parsing Error: {e}")
    return {
        "message": "Showing all Jira issues (Processed via fallback mode).",
        "data": issues,
    }