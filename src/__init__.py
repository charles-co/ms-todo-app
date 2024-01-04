import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if os.environ["STAGE"] == "test":
    try:
        from pytest_cov.embed import cleanup_on_sigterm
    except ImportError:
        pass
    else:
        cleanup_on_sigterm()
