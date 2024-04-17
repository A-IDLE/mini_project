
from dotenv import load_dotenv
from pathlib import Path

from fastapi import FastAPI, Request
from app.services.summarize import summary_news, summaryDTO
from fastapi.templating import Jinja2Templates


env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = FastAPI()

# html 템플릿 폴더를 지정하여 jinja템플릿 객체 생성
templates = Jinja2Templates(directory="templates")


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
