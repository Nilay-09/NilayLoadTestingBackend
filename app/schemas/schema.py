from pydantic import BaseModel
from typing import List, Optional

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