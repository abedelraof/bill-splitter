import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.database import Base, engine
from backend.routers import auth, friends, bills, settings

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bill Splitter")

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(friends.router, prefix="/api/friends", tags=["friends"])
app.include_router(bills.router, prefix="/api/bills", tags=["bills"])
app.include_router(settings.router, prefix="/api/settings", tags=["settings"])

# Serve frontend static files
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
