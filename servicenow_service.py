import os
import requests
from dotenv import load_dotenv

load_dotenv()

SERVICENOW_INSTANCE_URL = os.getenv("SERVICENOW_INSTANCE_URL")
SERVICENOW_USERNAME = os.getenv("SERVICENOW_USERNAME")
SERVICENOW_PASSWORD = os.getenv("SERVICENOW_PASSWORD")
def update_incident(incident_sys_id: str, decision: str, message: str):
    url = f"{SERVICENOW_INSTANCE_URL}/api/now/table/incident/{incident_sys_id}"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    if decision == "respond":
        body = {
            "work_notes": message,
            "close_notes": message,
            "close_code": "Solved (Permanently)",
            "state": "6"
        }
    elif decision == "ask":
        body = {
            "comments": message
        }
    elif decision == "escalate":
        body = {
            "work_notes": f"Escalated: {message}"
        }
    else:
        raise ValueError(f"Unknown decision: {decision}")

    response = requests.patch(
        url,
        auth=(SERVICENOW_USERNAME, SERVICENOW_PASSWORD),
        headers=headers,
        json=body,
        timeout=10
    )

    response.raise_for_status()
    return response.json()
if __name__ == "__main__":
    result = update_incident(
        incident_sys_id="c5b2519693c743102ad3f01bdd03d63a",
        decision="respond",
        message="Please try restarting the printer and unplugging the cable for 30 seconds."
    )
    print(result)