from aws_lambda_powertools import Logger
from bs4 import BeautifulSoup
from core.db.documents import ArticleDocument
from selenium.webdriver.common.by import By

from crawlers.base import BaseAbstractCrawler

logger = Logger(service="newton-llmcrawler")


class WikipediaCrawler(BaseAbstractCrawler):
    model = ArticleDocument

    # def set_extra_driver_options(self, options) -> None:
    #     options.add_argument(r"--profile-directory=Profile 2")

    def extract(self, link: str, **kwargs) -> None:
        logger.info(f"Starting scraping Wikipedia article: {link}")

        # Open the page
        self.driver.get(link)
        self.scroll_page()  # Optional for long articles, Wikipedia loads fast

        # Parse the page
        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        # Extract title and content
        title_tag = soup.find("h1", id="firstHeading")
        content_div = soup.find("div", id="mw-content-text")

        data = {
            "Title": title_tag.get_text(strip=True) if title_tag else None,
            "Content": content_div.get_text(separator="\n", strip=True) if content_div else None
        }

        logger.info(f"Successfully scraped article: {link}")

        # Close the driver
        self.driver.close()

        # Save to database
        instance = self.model(
            platform="wikipedia",
            content=data,
            link=link,
            author_id=kwargs.get("user")
        )
        instance.save()
        logger.info(f"Article saved to DB: {link}")



    def login(self):
        # """Log in to Medium with Google"""
        # self.driver.get("https://medium.com/m/signin")
        # self.driver.find_element(By.TAG_NAME, "a").click()
        pass