from fastapi import FastAPI
from .core.config import settings
from .features.canteen.router import router as canteen_router

app = FastAPI(
    title=settings.APP_NAME,
    description="Professional Canteen Recommendation System API",
    version="2.0.0",
    debug=settings.DEBUG
)

# Include Routers
app.include_router(canteen_router)

@app.get("/")
def health_check():
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "environment": "development" if settings.DEBUG else "production"
    }
