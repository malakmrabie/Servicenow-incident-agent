import threading
from typing import Optional

from fastapi import FastAPI, BackgroundTasks, status
from pydantic import BaseModel, Field

from gemini_service import get_decision
from servicenow_service import update_incident

app = FastAPI()

class IncidentPayload(BaseModel):
    incident_sys_id: str = Field(..., min_length=1)
    number: str = Field(..., min_length=1)
    short_description: str = Field(..., min_length=1)
    description: Optional[str] = ""
    priority: Optional[int] = None

_processed_incidents: set[str] = set()
_processed_lock = threading.Lock()

def process_incident(payload: dict):
    try:
        decision_data = get_decision(
            short_description=payload.get("short_description", ""),
            description=payload.get("description", "")
        )

        update_incident(
            incident_sys_id=payload["incident_sys_id"],
            decision=decision_data["decision"],
            message=decision_data["message"]
        )

        print(f"Processed {payload.get('number')}: {decision_data['decision']}")

    except Exception as e:
        with _processed_lock:
            _processed_incidents.discard(payload.get("incident_sys_id"))
        print(f"Error processing incident {payload.get('number')}: {e}")

@app.post("/webhook", status_code=status.HTTP_202_ACCEPTED)
async def receive_webhook(payload: IncidentPayload, background_tasks: BackgroundTasks):
    incident_id = payload.incident_sys_id

    with _processed_lock:
        if incident_id in _processed_incidents:
            return {"status": "duplicate_ignored", "incident_sys_id": incident_id}
        _processed_incidents.add(incident_id)

    background_tasks.add_task(process_incident, payload.model_dump())

    return {"status": "received", "number": payload.number} 