from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.endpoints import rfp, sales

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
# Set all CORS enabled origins (Allow All for Hackathon/Demo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (localhost:3000, Render, etc.)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rfp.router, prefix=f"{settings.API_V1_STR}/rfp", tags=["rfp"])
app.include_router(sales.router, prefix=f"{settings.API_V1_STR}/sales", tags=["sales"])

@app.get("/")
async def root():
    return {"message": "Welcome to B2B RFP Response Optimization API"}
