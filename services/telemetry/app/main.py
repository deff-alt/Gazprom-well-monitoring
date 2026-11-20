from fastapi import FastAPI
app = FastAPI(title="telemetry")

@app.get("/health")
def health():
    return {"status": "ok"}