import json
import re
import time
import logging
from pathlib import Path
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, Optional, Union

logger = logging.getLogger(__name__)

def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"

def save_json(obj: Any, path: Union[str, Path]) -> str:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
    return str(p.resolve())

def save_text(text: str, path: Union[str, Path]) -> str:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return str(p.resolve())

def clean_json_string(text: str) -> str:
    """Extracts JSON object or array from a string using regex."""
    text = text.strip()
    # Try to find a JSON object
    match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
    if match:
        return match.group(0)
    return text

def retry_operation(max_retries: int = 3, delay: float = 1.0):
    """Decorator for retrying operations with a simple delay."""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Error in {func.__name__} (attempt {attempt+1}/{max_retries}): {e}")
                    if attempt < max_retries - 1:
                        time.sleep(delay)
            logger.error(f"Operation {func.__name__} failed after {max_retries} attempts.")
            raise last_exception
        return wrapper
    return decorator
