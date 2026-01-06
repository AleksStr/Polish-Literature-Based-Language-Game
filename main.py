from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import fill_endpoint  

app = FastAPI(title="Game API")


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
    return {"message": "Game API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)