from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from router import api_router
from config import settings

description = (
    r"This Application will read group of .sta file converted to csv files and generate graphs and statistics"
)
title_name = r"UL Renewables-Windcube"
app = FastAPI(title=title_name, description=description)

origins = [
    settings.CLIENT_ORIGIN,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Router Definition
# ---------------------------
app.include_router(api_router, prefix="/api/windcube")
# app.mount("/", StaticFiles(directory="static", html=True), name="static")


