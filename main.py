from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from facebook_api import FacebookAPI

app = FastAPI()

origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class FacebookTokenRequest(BaseModel):
    app_id: str
    app_secret: str
    user_access_token: str
    page_id: str
    days_ago: int = 30


@app.post("/fetch-messages/")
def fetch_messages(data: FacebookTokenRequest):
    fb_api = FacebookAPI(
        app_id=data.app_id,
        app_secret=data.app_secret,
        user_access_token=data.user_access_token,
        page_id=data.page_id
    )

    if not fb_api.setup_tokens():
        return {"status": "error", "message": "Failed to set up tokens."}

    messages = fb_api.get_all_recent_messages(days_ago=data.days_ago)

    if messages:
        return {"status": "success", "messages": messages}
    else:
        return {"status": "error", "message": "No messages found."}
