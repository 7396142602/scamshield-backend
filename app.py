from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

# 1. Initialize FastAPI app
app = FastAPI(title="Scam Shield API")

# 2. Add CORS middleware (allows browser index.html to communicate)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Define Request Data Model
class SMSRequest(BaseModel):
    message: str

# 4. Sample training data
data = {
    'text': [
        "Congratulations! You won a $1000 gift card. Claim now!",
        "Hey, are we still meeting for lunch today?",
        "URGENT! Your account is locked. Click here to verify.",
        "Don't forget to buy milk on your way home.",
        "Free cash prize! Call this number immediately.",
        "Can you send me the report by 5 PM?"
    ],
    'label': [1, 0, 1, 0, 1, 0]  # 1 = Scam, 0 = Safe
}

df = pd.DataFrame(data)

# Train simple model
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(df['text'])
model = MultinomialNB()
model.fit(X, df['label'])

@app.post("/predict")
def predict_scam(sms: SMSRequest):
    vectorized_msg = vectorizer.transform([sms.message])
    prediction = model.predict(vectorized_msg)[0]
    is_scam = bool(prediction == 1)
    
    return {
        "message": sms.message,
        "is_scam": is_scam,
        "result": "SCAM DETECTED" if is_scam else "SAFE MESSAGE"
    }