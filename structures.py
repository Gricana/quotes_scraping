from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Tag:
    """
    Represents a quote tag with a name and URL.
    """
    name: str
    url: str


@dataclass
class Quote:
    """
    Represents a quotation with text and a list of associated tags.
    """
    text: str
    tags: List[Tag]


@dataclass
class Author:
    """
    Introduces the author of quotes with basic information:
    name, date of birth, place of birth, description,
    URL and list of citations.
    """
    name: str
    born_date: str = ""
    born_location: str = ""
    description: str = ""
    url: str = ""
    quotes: List[Quote] = field(default_factory=list)


# Data type for a JSON structure containing authors and their citations.
QuoteStructure = Dict[
    str,  # Author's name
    Dict[
        str,  # Author or Quote Fields
        str | List[Dict[str, str]]  # Author and citation field values
    ]
]
