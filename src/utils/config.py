from dotenv import load_dotenv
import os
load_dotenv()
class Setting:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    MODEL_NAME = "gemini-1.5-flash"

    MODEL_NAME = "gemini-1.5-flash"
    EMBEDDING_MODEL_NAME = "text-embedding-3-small"

    TEMPERATURE = 0.1
    MAX_TOKENS = 256
    TOP_K = 3

settings = Setting()