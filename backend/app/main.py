from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.endpoints import rfp, sales

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(rfp.router, prefix=f"{settings.API_V1_STR}/rfp", tags=["rfp"])
app.include_router(sales.router, prefix=f"{settings.API_V1_STR}/sales", tags=["sales"])

@app.get("/")
async def root():
    return {"message": "Welcome to B2B RFP Response Optimization API"}
