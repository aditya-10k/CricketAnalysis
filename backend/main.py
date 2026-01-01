from fastapi import FastAPI
from backend.api.player_replacement import router as player_replacement_router

app = FastAPI(
    title="Cricket Analysis API",
    version="1.0.0"
)

# Register API routes
app.include_router(player_replacement_router, prefix="/api")


@app.get("/")
def health_check():
    return {"status": "API is running"}
