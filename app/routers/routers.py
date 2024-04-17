from fastapi import APIRouter, Request, Form
from app.services.summarize import summarize_news
from app.services.crawling import crawling
from app.schemas.schemas import SearchQuery
from fastapi.templating import Jinja2Templates


router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.post("/summary")
async def summary_news_route(request: Request):
    # 요청 본문에서 텍스트 추출
    data = await request.json()
    text = data["text"]

    # 요약 함수 실행
    summary = await summarize_news(text)

    # 응답 JSON으로 변환
    response = {"summary": summary}

    return response


@router.post("/search")
async def search_news(request: Request):

    print("request")

    # 요청 본문에서 텍스트 추출
    data = await request.json()
    srcText = data["text"]

    print(srcText)

    # 몇개의 결과를 찾을 것인지
    srcCnt = 10

    # 요약 함수 실행
    search_result = await crawling(srcText, srcCnt)

    print(search_result)

    # 응답 JSON으로 변환
    response = {"articles": search_result}

    return response

    # return templates.TemplateResponse("index.html",
    #                                   {"articles": search_result})
