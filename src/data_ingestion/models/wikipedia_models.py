from pydantic import BaseModel
from datetime import datetime

class WikipediaContent(BaseModel):
    title: str
    content: str  # Clean text only
    url: str
    extracted_at: datetime = datetime.now()
