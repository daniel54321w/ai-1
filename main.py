import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import reviews, tools, redirect

app = FastAPI(
    title="אי של אמון — AI Marketplace API",
    description="פלטפורמת B2B לכלי AI לעסקים קטנים ובינוניים בישראל",
    version="0.1.0",
)

CORS_ORIGIN_REGEX = (
    r"https://(.*\.)?vercel\.app"
    r"|https://(.*\.)?netlify\.app"
    r"|https://ai\.co\.il"
    r"|http://localhost(:\d+)?"
    r"|http://127\.0\.0\.1(:\d+)?"
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=CORS_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["*"],
)

API = "/api/v1"
app.include_router(redirect.router, prefix=API)
app.include_router(tools.router,    prefix=API)
app.include_router(reviews.router,  prefix=API)

@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "ai-marketplace"}
