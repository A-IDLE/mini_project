from pydantic import BaseModel

# 뉴스 원문을 담을 DTO


class summaryDTO(BaseModel):
    newsChunk: str
