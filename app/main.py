from fastapi import FastAPI,HTTPException
from app.api.config.config import config_router
from fastapi.middleware.cors import CORSMiddleware

from app.automation.locust_runner import run_locust_test
from app.schemas.schema import Credentials,TestParameters
from app.config.config import set_credentials,set_dashboard_url,set_filter_config,set_visual_labels
from app.config.powerbi_config import get_access_token,config
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





@app.post("/set_credentials")
def set_creds(cred: Credentials):
    set_credentials(cred.email, cred.password)
    return {"message": "Credentials set successfully"}



@app.get("/get-access-token")
def get_token():
    token = get_access_token(config["power_bi_scopes"])
    if token is None:
        raise HTTPException(status_code=500, detail="Failed to obtain access token")
    return {"access_token": token}


@app.post("/run_test")
def run_test(params: TestParameters):
    
    
    if params.dashboard_url:
        set_dashboard_url(params.dashboard_url)
    if params.visuals:
        set_visual_labels(params.visuals)
    if params.filters:
        set_filter_config([f.dict() for f in params.filters])
        
    results = {}

    def target():
        nonlocal results
        results = run_locust_test(params.users, params.spawn_rate, params.run_time)
    
    test_thread = threading.Thread(target=target)
    test_thread.start()
    test_thread.join()
    
    if results:
        return results
    else:
        raise HTTPException(status_code=500, detail="Test failed or returned no results.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
