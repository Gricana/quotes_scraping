import asyncio
import json
from structures import QuoteStructure


class JSONSaver:
    """
    A class for async saving data to a JSON file.

    Methods:
        save (async): Async save data to a file.
        _write_to_file (static): Sync writes data to a file.
    """

    @staticmethod
    async def save(data: QuoteStructure, filename: str) -> None:
        """
        Async saves data to a JSON file,
        using the execution thread to perform the write operation.

        Parameters:
            data (QuoteStructure): Data to save.
            filename (str): File name to write data to.
        """
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, JSONSaver._write_to_file, data, filename)

    @staticmethod
    def _write_to_file(formatted_data: dict, filename: str) -> None:
        """
        Sync writes data to a JSON file.

        Parameters:
            formatted_data (dict): A dict that has a QuoteStructure structure.
            filename (str): File name to write data to.
        """
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(formatted_data, file, ensure_ascii=False, indent=4)
        print(f"Data saved in {filename}")
