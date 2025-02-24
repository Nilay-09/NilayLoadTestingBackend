# config.py
CREDENTIALS = {"email": None, "password": None}
VISUAL_LABELS = [] 
FILTER_CONFIG = [] 
DASHBOARD_URL = None


# CRED

def get_credentials():
    return CREDENTIALS["email"], CREDENTIALS["password"]

def set_credentials(email: str, password: str):
    global CREDENTIALS
    CREDENTIALS["email"] = email
    CREDENTIALS["password"] = password


# VISUAL GETTERS AND SETTERS

def set_visual_labels(labels: list):
    """Sets the global list of visual labels."""
    global VISUAL_LABELS
    VISUAL_LABELS = labels

def get_visual_labels():
    """Returns the global list of visual labels."""
    return VISUAL_LABELS


# FILTERS 

def set_filter_config(filter_list: list):
    global FILTER_CONFIG
    FILTER_CONFIG = filter_list

def get_filter_config():
    return FILTER_CONFIG


# DASHBOARD URL

def set_dashboard_url(url: str):
    global DASHBOARD_URL
    DASHBOARD_URL = url

def get_dashboard_url():
    return DASHBOARD_URL