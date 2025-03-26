# config.py

from dotenv import load_dotenv
import os



load_dotenv(override=True)



# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Rate Settings
PARALLEL_INSTANCES = 40
REQUESTS_PER_SECOND = 40
MAX_RETRIES = 10
RETRY_BACKOFF = 2

# Model Settings
GEMINI_MODEL = "openrouter/google/gemini-2.0-flash-lite-001"

# Image Settings
ZOOM_FACTOR = 1.5
CHUNK_SIZE = 40
OUTPUT_FORMAT = "jpeg"

# Files settings
INPUT_FOLDER = "Test"
OUTPUT_FOLDER = "out_test"
PARQUET_SIZE = 1420
FILE_NAMES = "train"  # train or test split ?