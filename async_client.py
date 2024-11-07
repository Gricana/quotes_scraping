import asyncio
import logging

import aiohttp

import config


class AsyncHttpClient:
    """
    Async HTTP client for making requests using a semaphore.

    Attributes:
        session (aiohttp.ClientSession): Session for making HTTP requests.
        semaphore (asyncio.Semaphore): Parallel request limiter.
    """

    def __init__(self):
        """
        Initializes the client with an empty session and a semaphore.
        """
        self.session = None
        self.semaphore = asyncio.Semaphore(config.SEMAPHORE_LIMIT)

    async def __aenter__(self):
        """
        An async context manager login method that initializes
        session for executing requests.

        Returns:
            AsyncHttpClient: A client instance with an active session.
        """
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """
        Async method for exiting the context manager, closing the session,
        if it was open.
        """
        if self.session:
            await self.session.close()

    async def fetch(self, url: str) -> str:
        """
        Makes an async HTTP request to the URL and returns text answer.

        Parameters:
            url (str): URL for the request.

        Returns:
            str: Response text if the request was successful,
            otherwise an empty string.

        Exceptions:
            RuntimeError: If the session has not yet been started.
        """
        if not self.session:
            raise RuntimeError("Session is not started yet.")

        async with self.semaphore:
            async with self.session.get(url) as response:
                if response.status != 200:
                    logging.error(f"Error {url} - code {response.status}")
                    return ""
                return await response.text()
