import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
from typing import List
import re
import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
import logging


# 환경변수 로드
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# 실행 무시를 위한 전역 변수
ignore_until = None


async def summarize_news(newsChunk: str):
    global ignore_until

    # 현재 시간
    current_time = datetime.now()

    # 실행 무시 로직
    if ignore_until is not None and current_time < ignore_until:
        return {"message": "요약 키워드가 모두 작성되어, 이후 키워드 업데이트가 생략됩니다."}

    # 뉴스 타이틀 문자열 정형화
    def clean_Chunk(news_Chunk):
        news_Chunk = news_Chunk.replace("\n", " ")
        clean_newsChunk = re.sub(
            r'[^가-힣A-Za-z0-9 .,!?~()%·\[\]]', '', news_Chunk)
        return clean_newsChunk

    cleaned_Chunk = clean_Chunk(newsChunk)

    # 데이터가 잘 정형화 됐는지 LOG
    logging.info(f"Received SummaryData: {cleaned_Chunk}")

    # Google API 키 호출
    google_api_key = os.getenv('GOOGLE_API_KEY')

    # ai프롬포트
    message_content = "내용을 바탕으로 오늘의 이슈 요약본을 작성해라. 내용만 작성한다. 주제별로 문단으로 나누어져 있어야 한다. ~습니다. 입니다. 로 끝나는 존칭이 담긴 정중한 어투여야 하고, 친절하게 말해야 한다. 인사와 날짜는 생략하고 본론만 이야기 해야 한다. 주제의 끝 마다 엔터를 두 번 작성해 단락을 끊어야 한다. 굵은 글씨(**)를 사용하지 않는다."

    # ai 모델: gemini-pro
    model = ChatGoogleGenerativeAI(
        model="gemini-pro", convert_system_message_to_human=True, temperature=0.3)

    # 정형화된 데이터 출력 및 AI 요약 생성
    try:
        result = model([
            SystemMessage(content=message_content),  # prompt
            HumanMessage(content=cleaned_Chunk)  # input data
        ])

        extracted_chunks = result.content

    # 에러 핸들링
    except Exception as e:
        print(f"Error during AI description generation: {e}")
        extracted_chunks = "Error"  # 예외가 발생한 경우, 여기에서 할당
        return {"message": "AI description generation failed", "error": str(e)}

    return extracted_chunks