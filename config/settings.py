"""All settings in one place. Values come from environment variables or the .env file."""
import os

from dotenv import load_dotenv

load_dotenv()  # reads .env if it exists; a real environment variable wins over it

BASE_URL = os.getenv("BASE_URL", "https://demoqa.com").rstrip("/")
API_URL = os.getenv("API_URL", "http://localhost:8080/parabank/services/bank").rstrip("/")
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
TIMEOUT = int(os.getenv("TIMEOUT", "10"))  # max seconds to wait for an element
