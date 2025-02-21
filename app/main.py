from fastapi import FastAPI,HTTPException
from app.api.config.config import config_router
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.automation.locust_runner import run_locust_test
import threading

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



class TestParameters(BaseModel):
    users: int = 10
    spawn_rate: int = 1
    run_time: int = 60 


@app.post("/run_test")
def run_test(params: TestParameters):
    results = {}

    def target():
        nonlocal results
        results = run_locust_test(params.users, params.spawn_rate, params.run_time)
    
    test_thread = threading.Thread(target=target)
    test_thread.start()
    test_thread.join()  # Wait for the test to complete
    
    if results:
        return results
    else:
        raise HTTPException(status_code=500, detail="Test failed or returned no results.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
