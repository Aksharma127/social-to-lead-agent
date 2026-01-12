from dataclasses import dataclass
from utils.logger import get_logger

logger = get_logger()


@dataclass
class Lead:
    name: str
    email: str
    platform: str


def mock_lead_capture(lead: Lead) -> bool:
    logger.info(f"Capturing lead: {{'name': lead.name, 'email': lead.email, 'platform': lead.platform}}")
    return True
