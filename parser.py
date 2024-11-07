import asyncio
import logging
from dataclasses import asdict

from bs4 import BeautifulSoup

import config
from async_client import AsyncHttpClient
from structures import *

# Setup logging for debugging and error handling.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)


class QuoteScraper:
    """
    Class for parsing quotes, information about authors,
    as well as the most popular tags.
    """

    def __init__(self):
        """
        Initializing the main class attrs.
        """
        self.aclient = None
        self.authors_data = {}
        self.top_tags = []

    async def fetch_quotes(self) -> None:
        """
        Loads pages with citations
        and adds them to the task list for processing.
        """
        page = 1
        tasks = []

        while True:
            url = f"{config.BASE_URL}/page/{page}/"
            logging.info(f"Loading quotes page {page}")
            html = await self.aclient.fetch(url)

            if "No quotes found!" in html:
                logging.info("End of quotes reached.")
                break

            tasks.append(self.process_quotes_page(html))
            page += 1

        logging.info("Processing of pages with citations has begun.")
        await asyncio.gather(*tasks)
        logging.info("Quote loading is complete.")

    async def process_quotes_page(self, html: str) -> None:
        """
        Processes the HTML content of a citation page,
        extracting citations and author information.
        """
        soup = BeautifulSoup(html, "html.parser")
        quotes_divs = soup.find_all("div", class_="quote")

        author_tasks = (
            self.process_quote_div(quote_div)
            for quote_div in quotes_divs
        )

        await asyncio.gather(*author_tasks)
        logging.info("The quotes page has been processed.")

    async def process_quote_div(self, quote_div) -> None:
        """
        Extracts quotation text, tags, and author information.
        """
        text = quote_div.find("span", class_="text").get_text()
        tags = (
            Tag(name=tag.get_text(),
                url=f"{config.BASE_URL}/tag/{tag.get_text()}/")
            for tag in quote_div.find_all("a", class_="tag")
        )

        author_name = quote_div.find("small", class_="author").get_text()
        author_url = config.BASE_URL + quote_div.find("a")["href"]

        quote = Quote(text=text, tags=list(tags))

        if author_name not in self.authors_data:
            self.authors_data[author_name] = Author(name=author_name)

        self.authors_data[author_name].quotes.append(quote)

        logging.info(f"Loading information about the author: {author_name}")
        await self.fetch_author(author_name, author_url)

    async def fetch_author(self, author_name: str, author_url: str) -> None:
        """
        Loads information about the author
        (date of birth, place of birth, description).
        """
        html = await self.aclient.fetch(author_url)
        if not html:
            logging.warning(f"Failed to load author data: {author_name}")
            return

        soup = BeautifulSoup(html, "html.parser")

        born_date = soup.find("span", class_="author-born-date").get_text()
        born_location = soup.find("span",
                                  class_="author-born-location").get_text()[3:]
        description = soup.find("div",
                                class_="author-description").get_text().strip()

        if author_name in self.authors_data:
            author = self.authors_data[author_name]
            updates = (
                ('born_date', born_date),
                ('born_location', born_location),
                ('description', description),
                ('url', author_url)
            )
            for key, value in updates:
                setattr(author, key, value)

            logging.info(f"Author information {author_name} "
                         f"has been successfully updated.")

    async def fetch_top_tags(self) -> None:
        """
        Loads popular tags from the main page of the site.
        """
        html = await self.aclient.fetch(config.BASE_URL)
        if not html:
            logging.error("Failed to load data for popular tags.")
            return

        soup = BeautifulSoup(html, "html.parser")
        tags_div = soup.find("div", class_="tags-box")
        if not tags_div:
            logging.error("The tag block could not be found.")
            return

        self.top_tags = (
            Tag(name=tag.get_text(),
                url=f"{config.BASE_URL}/tag/{tag.get_text()}/")
            for tag in tags_div.find_all("a", class_="tag")
        )

        logging.info("Popular tags loaded successfully.")

    async def scrape_all(self) -> QuoteStructure:
        """
        The main method for starting the process of parsing all data.
        Returns the resulting data structure with authors and tags.
        """
        logging.info("Start collecting all data from the site.")
        async with AsyncHttpClient() as self.aclient:
            await self.fetch_quotes()
            await self.fetch_top_tags()

        logging.info("All data collection is complete.")
        return {
            "authors": {
                author_name: asdict(author)
                for author_name, author in self.authors_data.items()
            },
            "top_tags": [asdict(tag) for tag in self.top_tags]
        }
