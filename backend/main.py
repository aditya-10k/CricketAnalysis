from fastapi import FastAPI

app = FastAPI(title="Cricket Analysis API")

@app.get("/")
def health():
    return {"status": "FastAPI backend is running"}
