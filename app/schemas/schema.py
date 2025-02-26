from pydantic import BaseModel
from typing import List, Optional,Dict,Any

class FilterConfig(BaseModel):
    label: str
    value: str


class TestParameters(BaseModel):
    users: int = 10
    spawn_rate: int = 1
    run_time: int = 60 
    dashboard_url: Optional[str] = None
    visuals: Optional[List[str]] = None
    filters: Optional[List[FilterConfig]] = None
    
    
class Credentials(BaseModel):
    email: str
    password: str
    
    
    
    
class Summary(BaseModel):
    users_completed: int
    total_requests: int
    total_failures: int
    average_response_time_ms: float
    min_response_time_ms: Optional[float]
    max_response_time_ms: float

class UserResult(BaseModel):
    dashboard_load_time: float
    visual_load_times: Dict[str, float] 
    filter_apply_times: Dict[str, float] 
    total_time: float
    error: Optional[str] = None

class APIRequest(BaseModel):
    summary: Dict[str, Any] 
    user_results: List[Dict[str, Any]]