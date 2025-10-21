from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.middleware import audit_middleware
from app.api.v1 import webhooks, cases, documents, lawyers, payments, calendar, analytics
from app.core.database import engine
from app.models import Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Legal Intake API", version="1.0.0")

# Middleware
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])
app.add_middleware(audit_middleware)

# Routes
app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["WhatsApp"])
app.include_router(cases.router, prefix="/api/v1/cases", tags=["Cases"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(lawyers.router, prefix="/api/v1/lawyers", tags=["Lawyers"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["Payments"])
app.include_router(calendar.router, prefix="/api/v1/calendar", tags=["Calendar"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])

@app.get("/health")
async def health_check():
    return {"status": "healthy"}