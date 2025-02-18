from fastapi import FastAPI
from app.api.config.config import config_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Load Testing Tool", version="1.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)


# Include routers from our endpoints
app.include_router(config_router, prefix="/config", tags=["Config"])

@app.get("/")
def root():
    return {"message": "Welcome to the Load Testing Tool API"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
