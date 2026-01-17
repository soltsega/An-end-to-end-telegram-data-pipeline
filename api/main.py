from fastapi import FastAPI

app = FastAPI(title="Medical Telegram Warehouse API")

@app.get("/")
async def root():
    return {"message": "Welcome to the Medical Telegram Warehouse API"}
