import requests
from bs4 import BeautifulSoup
from models.wikipedia_models import WikipediaContent

class SimpleWikipediaExtractor:
    def __init__(self):
        self.headers = {'User-Agent': 'NewtonAI-Bot/1.0 (Educational; student@example.com)'}
    
    def extract_page(self, page_title: str) -> WikipediaContent:
        """Get clean text from Wikipedia page"""
        url = f"https://en.wikipedia.org/w/api.php"
        params = {
            'action': 'parse',
            'page': page_title,
            'format': 'json',
            'prop': 'text|displaytitle'
        }
        
        response = requests.get(url, params=params, headers=self.headers, timeout=15)
        data = response.json()
        
        # Clean HTML to text
        soup = BeautifulSoup(data['parse']['text']['*'], 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'table', 'div.navbox', 'div.infobox']):
            element.decompose()
        
        clean_text = soup.get_text()
        clean_text = ' '.join(clean_text.split())  # Clean whitespace
        
        return WikipediaContent(
            title=data['parse']['displaytitle'],
            content=clean_text,
            url=f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}"
        )
