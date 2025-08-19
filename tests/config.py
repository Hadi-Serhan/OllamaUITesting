import os

OLLAMA_URL   = os.getenv("OLLAMA_URL", "http://localhost:3000")
HEADLESS     = os.getenv("HEADLESS", "false").lower() == "true"
BROWSER      = os.getenv("BROWSER", "chrome").lower()
SCREEN_WIDTH = int(os.getenv("SCREEN_WIDTH", "1920"))
SCREEN_HEIGHT= int(os.getenv("SCREEN_HEIGHT", "1080"))
MODEL_NAME   = (os.getenv("MODEL_NAME") or "").strip() or None
CHROME_BIN   = os.getenv("CHROME_BIN") or None
FIREFOX_BIN  = os.getenv("FIREFOX_BIN") or None
WAIT_TIMEOUT = int(os.getenv("WAIT_TIMEOUT", "60"))