import logging
from rich.logging import RichHandler

from datetime import datetime


now = datetime.now()
filename = now.strftime("%a%d%B_%H%M_%S")


# Configure RichHandler
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, markup=True)]
)

# Create your logger instance
logger = logging.getLogger("app_logger")

# Optional: adjust level per logger if needed
logger.setLevel(logging.DEBUG)

# Create a FileHandler for file output, excluding DEBUG messages
file_handler = logging.FileHandler(f"logs/{filename}_run.log")
file_handler.setLevel(logging.INFO)  # Exclude DEBUG messages

# Create a formatter and set it for the FileHandler
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
file_handler.setFormatter(formatter)

# Add the FileHandler to the logger
logger.addHandler(file_handler)