import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import fill_endpoint

app = FastAPI(title="Game API")


port = int(os.environ.get("PORT", 8080))


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(fill_endpoint.router)

@app.get("/")
async def root():
    return {"message": "Game API on Cloud Run", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)