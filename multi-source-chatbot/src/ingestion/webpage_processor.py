import aiohttp
from bs4 import BeautifulSoup
from src.logger import logger


class WebPageProcessor:
    @staticmethod
    async def fetch_page(url: str) -> str:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        raise Exception(f"HTTP {response.status}: {url}")
                    return await response.text()
        except Exception as e:
            logger.error(f"Error fetching webpage {url}: {e}")
            raise
    
    @staticmethod
    def extract_content(html: str) -> str:
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            for tag in soup(['script', 'style', 'nav', 'footer']):
                tag.decompose()
            
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            logger.error(f"Error extracting webpage content: {e}")
            raise
    
    @staticmethod
    async def fetch_and_extract(url: str) -> str:
        html = await WebPageProcessor.fetch_page(url)
        return WebPageProcessor.extract_content(html)
