import os
import logging
import requests
from dotenv import load_dotenv
from urllib.parse import urlencode

# Configure logging with timestamps
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

config = {
    "client_id": os.getenv("CLIENT_ID"),
    "client_secret": os.getenv("CLIENT_SECRET"),
    "tenant_id": os.getenv("TENANT_ID"),
    "username": os.getenv("UserId"),
    "password": os.getenv("PASSWORD"),
    "authority": os.getenv("AUTHORITY"),
    "user_scopes": ["Chat.ReadWrite", "User.Read"],
    "power_bi_scopes": os.getenv("POWER_BI_SCOPES", "").split(), 
    "sendgrid_api_key": os.getenv("SENDGRID_API_KEY"),
}

def get_access_token(scopes):
    """
    Obtains an access token using the password grant type.
    
    :param scopes: A list of scopes.
    :return: The access token if successful, or None otherwise.
    """
    url = f"{config['authority']}/oauth2/v2.0/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "password",
        "client_id": config["client_id"],
        "client_secret": config["client_secret"],
        "username": config["username"],
        "password": config["password"],
        "scope": " ".join(scopes),
    }

    logger.info(f"Request URL: {url}")
    logger.info(f"Request Headers: {headers}")
    logger.info(f"Request Body: {urlencode(data)}")

    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json().get("access_token")
    except Exception as error:
        logger.error(f"Failed to obtain access token: {error}")
        if hasattr(error, 'response') and error.response is not None:
            logger.error(f"Response: {error.response.text}")
        return None

if __name__ == "__main__":

    token = get_access_token(config["power_bi_scopes"])
    if token:
        logger.info(f"Access Token: {token}")
    else:
        logger.error("No token received.")
