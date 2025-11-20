import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import settings

if __name__ == "__main__":
    settings.ensure_dirs()
    
    import uvicorn
    from src.api.main import app
    
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        log_level=settings.LOG_LEVEL.lower()
    )
