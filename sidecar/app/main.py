"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, parse, query
from app.config import settings
from app.logging import setup_logging
from app.pipeline.controller import PipelineController
from app.storage.document_store import DocumentStore
from app.storage.filesystem import FileSystemDocumentStore

# Setup logging
setup_logging()

# Initialize global components
pipeline_controller = PipelineController()

# Use file-based storage for persistence
document_store = FileSystemDocumentStore()

# Inject document store into query module
query.set_document_store(document_store)

# Inject document store into parse module
parse.set_document_store(document_store)

# Create FastAPI app
app = FastAPI(
    title="Aletheia Sidecar",
    description="Local perceptual daemon for document and image parsing",
    version="0.1.0",
    docs_url="/docs" if settings.environment == "development" else None,
    redoc_url="/redoc" if settings.environment == "development" else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.environment == "development" else settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(parse.router, prefix="/api/v1", tags=["parse"])
app.include_router(query.router, prefix="/api/v1", tags=["query"])


@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup."""
    # Log startup info
    from app.logging import get_logger
    logger = get_logger(__name__)
    logger.info(f"Aletheia Sidecar starting on {settings.host}:{settings.port}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Document store: {document_store.count()} documents loaded")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown."""
    # File-based store persists automatically, no cleanup needed
    pass


# Export for external access
def get_document_store() -> FileSystemDocumentStore:
    """Get the global document store."""
    return document_store


def get_pipeline_controller() -> PipelineController:
    """Get the global pipeline controller."""
    return pipeline_controller
