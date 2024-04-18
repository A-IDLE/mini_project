from fastapi import APIRouter, Request, Form, Depends
from app.services.summarize import summarize_news
from app.services.crawling import crawling
from app.schemas.schemas import SearchQuery
from fastapi.templating import Jinja2Templates
from app.routers.models import News
from app.routers.database import engine, SessionLocal
from sqlalchemy.orm import Session

# 여기서 데이터베이스 생성
# models.Base.metadata.create_all(bind=engine)

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/summary")
async def summary_news_route(request: Request,db: Session = Depends(get_db)):
    # 요청 본문에서 텍스트 추출
    data = await request.json()
    newsChunk = data["text"]
    link = data["link"]

    # 해당 뉴스 요약이 이미 있는지 확인합니다.
    existing_news = db.query(News).filter(News.link == link).first()
    if existing_news.summarized_text:
        print("요약 있다")
        summary = existing_news.summarized_text
    else:
        # 요약 함수 실행
        summary = await summarize_news(newsChunk)
        existing_news.summarized_text = summary
    # 변경사항을 커밋합니다.
    db.commit()

    print(summary)

    # 응답 JSON으로 변환
    response = {"summary": summary}

    return response


@router.post("/search")
async def search_news(request: Request,db: Session = Depends(get_db)):

    print("request")

    # 요청 본문에서 텍스트 추출
    data = await request.json()
    srcText = data["text"]

    print(srcText)

    # 몇개의 결과를 찾을 것인지
    srcCnt = 3

    # 요약 함수 실행
    search_result = await crawling(srcText, srcCnt)

    for article in search_result:
        # 해당 뉴스가 이미 있는지 확인합니다.
        existing_news = db.query(News).filter(News.link == article['link']).first()
        if existing_news:
            print(article['emotion'])
        else:
            # news 테이블에 새로운 레코드를 추가합니다.
            add_news = News(title=article['title'], description=article['description'], org_link=article['org_link'], link=article['link'], full_text=article['full_text'][:10000], keyword=srcText, emotion=article['emotion'], postive_percent=article['postive_percent'], negative_percent=article['negative_percent'])
            db.add(add_news)
    # 변경사항을 커밋합니다.
    db.commit()
    # 응답 JSON으로 변환
    response = {"articles": search_result}

    return response

    # return templates.TemplateResponse("index.html",
    #                                   {"articles": search_result})
