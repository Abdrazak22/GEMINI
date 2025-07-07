# FILE: backend/main.py
import os
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()

app = FastAPI()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
CUSTOM_SEARCH_ENGINE_ID = os.getenv("CUSTOM_SEARCH_ENGINE_ID")

# This allows your frontend (on Vercel) to talk to your backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For simplicity, allow all. For production, restrict to your Vercel URL.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchQuery(BaseModel):
    query: str

@app.post("/api/search")
async def search_pdfs(search: SearchQuery):
    try:
        refined_query = f"{search.query} filetype:pdf"
        service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
        res = service.cse().list(
            q=refined_query,
            cx=CUSTOM_SEARCH_ENGINE_ID,
            num=10
        ).execute()

        results = []
        if 'items' in res:
            for item in res['items']:
                if item.get('fileFormat') == 'application/pdf' or '.pdf' in item.get('link'):
                    results.append({
                        "title": item.get('title'),
                        "link": item.get('link'),
                        "source": item.get('displayLink'),
                        "snippet": item.get('snippet'),
                    })
        return {"results": results}
    except Exception as e:
        return {"error": str(e)}, 500

# This file tells hosting services what Python libraries to install.
@app.get("/")
def read_root():
    return {"status": "PDFScope Backend is running"}
