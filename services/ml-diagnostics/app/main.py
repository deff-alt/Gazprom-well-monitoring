from fastapi import FastAPI
app = FastAPI(title="ml-diagnostics")

@app.get("/health")
def health():
    return {"status": "ok"}
