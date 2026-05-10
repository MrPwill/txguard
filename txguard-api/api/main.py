from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers import transactions, alerts, reports, model
from .database import engine, Base

# Create tables (for production, use migrations like Alembic)
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Database connection failed, tables not created: {e}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(transactions.router, prefix=settings.API_V1_STR)
app.include_router(alerts.router, prefix=settings.API_V1_STR)
app.include_router(reports.router, prefix=settings.API_V1_STR)
app.include_router(model.router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Welcome to TxGuard AI API", "version": settings.VERSION}

@app.get("/health")
async def health():
    return {"status": "healthy"}
