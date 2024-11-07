from config import RESULT_FILE
from parser import QuoteScraper
from saver import JSONSaver


async def main():
    scraper = QuoteScraper()
    data = await scraper.scrape_all()
    await JSONSaver.save(data, RESULT_FILE)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
