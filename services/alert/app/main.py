from fastapi import FastAPI
app = FastAPI(title="alert")

@app.get("/health")
def health():
    return {"status": "ok"}
