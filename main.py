from fastapi import FastAPI, File, HTTPException, Response, UploadFile, Form, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from fastapi.templating import Jinja2Templates
import cv2
import numpy as np
import base64
from pydantic import BaseModel

fastapi_app = FastAPI()

templates = Jinja2Templates(directory="templates")

fastapi_app.mount("/templates", StaticFiles(directory="templates"), name="templates")

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
        raise HTTPException(status_code=400, detail="No text provided for summarization")

    # positive_summary = f"긍정적 요약: {title[:500]}..."
    # negative_summary = f"부정적 요약: {title[-500:]}..."
    pos = "긍" * 1000
    neg = "부" * 1000
    positive_summary = f"긍정적 요약: 긍..." + pos
    negative_summary = f"부정적 요약: 부..." + neg
    result_links = "http://example.com"  # Implement logic to generate result links here

    summary_response = SummaryResponse(
        positive_summary=positive_summary,
        negative_summary=negative_summary,
        result_links=result_links
    )

    html_content = templates.TemplateResponse("index.html", {"request": request, "summary_response": summary_response})
    return Response(content=html_content.body, media_type="text/html")



if __name__ == "__main__":
    uvicorn.run('main:fastapi_app',
                host='localhost', port=8000, reload=True)
