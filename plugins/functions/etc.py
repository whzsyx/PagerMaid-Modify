import logging
from typing import Any, Callable, Optional, Union
from threading import Thread, Timer


def delay(secs: int, target: Callable, args: list = None) -> bool:
    # Call a function with delay
    result = False

    try:
        t = Timer(secs, target, args)
        t.daemon = True
        result = t.start() or True
    except Exception as e:
        logger.warning(f"Delay error: {e}", exc_info=True)

    return result
