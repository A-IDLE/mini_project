from pydantic import BaseModel


class summaryDTO(BaseModel):
    newsChunk: str


class SearchQuery(BaseModel):
    title: str
