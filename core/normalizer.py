def normalize_jira_data(raw_issues: list) -> list:
  """Flattens nested Jira JSON into clean tabular records using pure Python."""
  formatted_rows = []
  for issue in raw_issues:
    fields = issue.get("fields", {})
    formatted_rows.append({
        "key": issue.get("key"),
        "summary": fields.get("summary", ""),
        "status": fields.get("status", {}).get("name", "Unknown"),
        "priority": fields.get("priority", {}).get("name", "Medium"),
        "assignee": fields.get("assignee", {}).get("displayName", "Unassigned"),
        "issue_type": fields.get("issuetype", {}).get("name", "Task"),
        "created": fields.get("created", "")[:10],
    })
  return formatted_rows