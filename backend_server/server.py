import argparse
import os
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend_server.database import init_db
from backend_server.server.routes import auth, feedback, personas, providers, simulation, templates


# Initialize database on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

router = APIRouter(prefix="/api")

router.include_router(auth.router, tags=["auth"])
router.include_router(simulation.router, tags=["simulation"])
router.include_router(templates.router, tags=["templates"])
router.include_router(personas.router, tags=["personas"])
router.include_router(feedback.router, tags=["feedback"])
router.include_router(providers.router, tags=["providers"])

app.include_router(router)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the FastAPI server")
    # parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    # parser.add_argument("--port", type=int, default=11544, help="Port to bind to")
    parser.add_argument("--dev", action="store_true", help="Run in development mode")
    args = parser.parse_args()
    host = os.environ.get("LISTEN_ADDRESS", "0.0.0.0")
    port = int(os.environ.get("BACKEND_PORT", 11544))

    if args.dev:
        uvicorn.run(
            "__main__:app", host=host, port=port, reload=True, reload_includes="*.py", reload_excludes="storage"
        )
    else:
        uvicorn.run(app, host=host, port=port)
