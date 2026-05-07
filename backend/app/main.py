from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import users, auth, invitations, admin, role_tree, fillout, projects, credits, waiting_list
from .database import init_db
import os
from dotenv import load_dotenv
import logging
import sys
import logging.handlers
from fastapi.staticfiles import StaticFiles
from .core.constants import AVATARS_DIR

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(title="Fibonacci Social API")

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    logger.info("Database initialized")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"]) 
app.include_router(invitations.router, prefix="/api/invitations", tags=["invitations"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(role_tree.router, prefix="/api/role-tree", tags=["role-tree"])
app.include_router(fillout.router, prefix="/api/fillout", tags=["fillout"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(credits.router, prefix="/api/credits", tags=["credits"])
app.include_router(waiting_list.router, prefix="/api/waiting-list", tags=["waiting-list"])

# Mount uploads directory
app.mount("/avatars", StaticFiles(directory=AVATARS_DIR), name="avatars")