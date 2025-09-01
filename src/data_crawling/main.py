from typing import Any
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from core import lib
from core.db.documents import ArticleDocument
from crawlers.wikipedia import WikipediaCrawler

logger = Logger(service="newton-llm/crawler")


def handler(event: dict[str, Any], context: LambdaContext | None = None) -> dict[str, Any]:
    link = event.get("link")
    if not link:
        return {"statusCode": 400, "body": "Missing 'link' in event"}

    crawler = WikipediaCrawler()

    try:
        # Crawl Wiki Page
        content = crawler.extact(link=link)

        #save into mongodb
        article = ArticleDocument(
            platform="wikipedia",
            link=link,
            content=content,
            auther_id="system"
        )

        article.save()

        return {"statusCode": 200, "body": "Wikipedia link processed successfully"}
    
    except Exception as e:
        logger.exception("Crawler failed")
        return {"statusCode": 500, "body": f"An error occured: {str(e)}"}

if __name__ == "__main__":
    event = {
        "link": "https://en.wikipedia.org/wiki/Isaac_Newton",
    }
    response = handler(event, None)
    print(response)