# ServiceNow Incident Agent

This is my Task 0 project for the Sprints x BARQ Systems AI Engineering internship.

Basically, when someone opens a new incident on ServiceNow, my service gets notified automatically, sends the ticket to Gemini to figure out what to do with it, and then writes the answer back on the same ticket. No manual steps anywhere in between.

## The flow

1. New incident gets created in ServiceNow.
2. A Business Rule I set up fires automatically and sends the incident data to my FastAPI service.
3. My service builds a prompt with the ticket info + 5 knowledge base articles and asks Gemini to decide: respond, ask, or escalate.
4. Whatever Gemini decides gets written back onto that same ticket.

Depending on the decision:
- **respond** → the solution gets added and the ticket is closed
- **ask** → a clarifying question gets added as a comment
- **escalate** → a work note gets added saying it needs a human

## Folder structure

I put my actual code in `src/` and kept the stuff that was given to me for the task in `assets/`, just so it's clear what I built vs what came with the assignment.

- `src/main.py` - the FastAPI app, has the /webhook endpoint and a guard so the same ticket doesn't get processed twice
- `src/gemini_service.py` - loads the prompt and calls Gemini
- `src/servicenow_service.py` - sends the PATCH request back to ServiceNow
- `src/prompt.txt` - the prompt I send to Gemini, exactly as it's sent
- `assets/pdi_guide.md` - the guide for setting up the ServiceNow PDI
- `assets/business_rule.js` - the script that goes into the ServiceNow Business Rule
- `assets/kb_articles.json` - the 5 articles Gemini is allowed to use
- `assets/test_incidents.json` - the 3 tickets used to test each decision type

## What you need before running this

- Python 3.11+
- A ServiceNow PDI (free, from developer.servicenow.com)
- A Gemini API key (free, from Google AI Studio)
- ngrok, or something similar to get a public URL

## Running it

Clone it and go inside:
```
git clone https://github.com/malakmrabie/Servicenow-incident-agent.git
cd Servicenow-incident-agent
```

Set up a virtual env and install everything:
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your own values (Gemini key, your PDI URL, admin username/password).

Run the service:
```
uvicorn src.main:app --reload --port 8000
```

Then in another terminal, expose it:
```
ngrok http 8000
```

Grab the ngrok URL it gives you. You'll need to paste it (with `/webhook` at the end) into the Business Rule on your PDI - the full steps for that are in `assets/pdi_guide.md`.

Note: the ngrok URL changes every time you restart it, so if you stop and restart, you have to update the Business Rule again with the new URL.

## Testing

I tested it two ways. First just hitting the endpoint directly to make sure it responds:
```
curl -X POST http://localhost:8000/webhook -H "Content-Type: application/json" -d @src/test_payload.json
```

And then the real test - creating the 3 tickets from `assets/test_incidents.json` directly on the PDI and checking each one landed on the right decision:
- "Printer not printing after office move" → respond
- "Cannot send email" (no real details) → ask
- "Request: annual leave approval" → escalate

## A few things I ran into

Getting the prompt right took a few tries. At first Gemini kept choosing "respond" any time the ticket mentioned a topic that matched a KB article title, even if there wasn't actually enough info to confirm the fix would work. I had to rewrite the prompt to be explicit that just matching the topic isn't enough, and add a couple of examples so it understood the difference between "respond" and "ask". After that it worked consistently across the test cases.

Also worth knowing: the duplicate-ticket check is just an in-memory set, so if I restart the service it forgets which tickets it already processed. That's fine for this project but wouldn't be enough for something real.

More on what was hard and what I'd do differently is in the reflection file.
