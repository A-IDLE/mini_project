import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, Request
from summary_news import summary_news, summaryDTO
from fastapi.templating import Jinja2Templates


env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = FastAPI()

# html 템플릿 폴더를 지정하여 jinja템플릿 객체 생성
templates = Jinja2Templates(directory="templates")

# current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# @app.get("/java-connection-test")
# async def java_connection_test():
#     print("java 서버와 연결되어 있습니다.", f"{current_time}")
#     return {"message": "Python 서버와 연결되어 있습니다. " + current_time}

# @app.post("/receive-news")
# async def receive_news_route(news: NewsDTO):
#     return await receive_news(news)

# @app.post("/process-news")
# async def process_news_route(news: NewsDTO):
#     return await process_news(news)

# @app.post("/keyword-news")
# async def receive_titles(news: keywordNewsDTO):
#     return await keyword_news(news.titles, news.keywordNewsCode)


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html",
                                      {"request": request})


@app.post("/summary")
async def summary_news_route(request: Request):
    # 요청 본문에서 텍스트 추출
    data = await request.json()
    text = data["text"]

    # 요약 함수 실행
    summary = await summary_news(text)

    # 응답 JSON으로 변환
    response = {"summary": summary}

    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
