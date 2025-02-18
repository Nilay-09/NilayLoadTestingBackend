import psutil
import platform
from fastapi import FastAPI,APIRouter
from pydantic import BaseModel

config_router = APIRouter()

class SystemInfo(BaseModel):
    total_ram: int
    used_ram: int
    total_space: int
    used_space: int
    processor_info: str
    os_name: str

@config_router.get("/system_info", response_model=SystemInfo)
def get_system_info():
    # Get RAM information
    ram_info = psutil.virtual_memory()
    total_ram = ram_info.total
    used_ram = ram_info.used

    # Get disk space information
    disk_info = psutil.disk_usage('/')
    total_space = disk_info.total
    used_space = disk_info.used

    # Get processor information
    processor_info = platform.processor()

    # Get OS name
    os_name = platform.system()

    system_info = SystemInfo(
        total_ram=total_ram,
        used_ram=used_ram,
        total_space=total_space,
        used_space=used_space,
        processor_info=processor_info,
        os_name=os_name
    )

    return system_info

