from fastapi import FastAPI, HTTPException, Response, Form, Request
from fastapi.staticfiles import StaticFiles
import uvicorn
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from dotenv import load_dotenv
from pathlib import Path
import app.routers.models

from app.routers.routers import router

fastapi_app = FastAPI()

# Mount the router
fastapi_app.include_router(router)

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Mount the icons directory as a StaticFiles
fastapi_app.mount(
    "/icons", StaticFiles(directory="icons"), name="icons"
)

templates = Jinja2Templates(directory="templates")

fastapi_app.mount(
    "/templates", StaticFiles(directory="templates"), name="templates")

# Response model


class SummaryResponse(BaseModel):
    positive_summary: str
    negative_summary: str
    result_links: str

# 메인화면


@fastapi_app.get("/")
def home(request: Request):

    positive_summary = f"긍정적 요약:..."
    negative_summary = f"부정적 요약: ..."
    result_links = "http://example.com"  # 여기에 결과 링크를 반환하는 로직을 구현하십시오.

    summary_response = SummaryResponse(
        positive_summary=positive_summary,
        negative_summary=negative_summary,
        result_links=result_links
    )

    return templates.TemplateResponse("index.html",
                                      {"request": request, "summary_response": summary_response})


@fastapi_app.post("/review-summary/")
async def generate_summary(request: Request, title: str = Form(...)):
    print(title)
    if not title:
        raise HTTPException(
            status_code=400, detail="No text provided for summarization")

    # positive_summary = f"긍정적 요약: {title[:500]}..."
    # negative_summary = f"부정적 요약: {title[-500:]}..."
    pos = "긍" * 1000
    neg = "부" * 1000
    positive_summary = f"긍정적 요약: 긍..." + pos
    negative_summary = f"부정적 요약: 부..." + neg
    # Implement logic to generate result links here
    result_links = "http://example.com"

    summary_response = SummaryResponse(
        positive_summary=positive_summary,
        negative_summary=negative_summary,
        result_links=result_links
    )

    html_content = templates.TemplateResponse(
        "index.html", {"request": request, "summary_response": summary_response})
    return Response(content=html_content.body, media_type="text/html")


if __name__ == "__main__":
    uvicorn.run('main:fastapi_app',
                host='localhost', port=9000, reload=True)
