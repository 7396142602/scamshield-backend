import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI()

# Allows your HTML page to connect to your Python code
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MessageRequest(BaseModel):
    message: str

# Loads the webpage when you open the browser
@app.get("/")
def home():
    return FileResponse("index.html")

# Scam detection rules
URGENCY_PATTERNS = [r"\burgent\b", r"\bimmediate(ly)?\b", r"\bsuspend(ed)?\b", r"\block(ed)?\b", r"\bexpire(s|d)?\b"]
FINANCIAL_PATTERNS = [r"\bbank\b", r"\baccount\b", r"\botp\b", r"\bverify\b", r"\bkyc\b", r"\bwinner\b", r"\bprize\b"]
LINK_PATTERNS = [r"https?://\S+", r"bit\.ly/\S+", r"tinyurl\.com/\S+"]

@app.post("/analyze")
def analyze_message(payload: MessageRequest):
    text = payload.message
    if not text.strip():
        raise HTTPException(status_code=400, detail="Message empty")

    score = 0
    indicators = []

    if any(re.search(p, text, re.IGNORECASE) for p in URGENCY_PATTERNS):
        score += 35
        indicators.append("Uses urgent or panic-inducing words")

    if any(re.search(p, text, re.IGNORECASE) for p in FINANCIAL_PATTERNS):
        score += 30
        indicators.append("Asks for banking, OTP, or sensitive info")

    if any(re.search(p, text, re.IGNORECASE) for p in LINK_PATTERNS):
        score += 35
        indicators.append("Contains a suspicious web link")

    score = min(score, 100)
    risk_level = "High" if score >= 60 else "Medium" if score >= 30 else "Low"

    return {
        "risk_score": score,
        "risk_level": risk_level,
        "is_suspicious": score >= 40,
        "detected_indicators": indicators
    }