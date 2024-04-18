import os
import urllib.request
import datetime
import json
import requests
from bs4 import BeautifulSoup
import json
import torch
import math

from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer

model_name = "jaehyeong/koelectra-base-v3-generalized-sentiment-analysis"
model = AutoModelForSequenceClassification.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# 파이프라인 생성
classifier = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')

# url request
def getRequestUrl(url):
    req = urllib.request.Request(url)
    req.add_header("X-Naver-Client-Id", client_id)
    req.add_header("X-Naver-Client-Secret", client_secret)

    try:
        response = urllib.request.urlopen(req)
        if response.getcode() == 200:
            print("[%s] Url Request Success" % datetime.datetime.now())
            return response.read().decode('utf-8')
    except Exception as e:
        print(e)
        print("[%s] Error for URL : %s" % (datetime.datetime.now(), url))
        return None

# naver search
def getNaverSearch(node, srcText, start, display, emotion, pubDate):
    base = "https://openapi.naver.com/v1/search"
    node = "/%s.json" % node
    parameters = "?query=%s&start=%s&display=%s&emotion=%s&pubDate%s" % (
        urllib.parse.quote(srcText), start, display, urllib.parse.quote(str(emotion)), pubDate)

    url = base + node + parameters
    responseDecode = getRequestUrl(url)

    if (responseDecode is None):
        return None
    else:
        return json.loads(responseDecode)

# get full article
def get_full_article(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            content = soup.find('div', {'id': 'newsct_article'}).text
            return content.strip()
    except Exception as e:
        print(f"Error retrieving article from {url}: {e}")
        return None

# 수정된 함수
async def crawling(srcText: str, srcCnt: int):
    node = 'news'  # 크롤링 할 대상
    srcText = srcText
    cnt = 0
    jsonResult = []
    start = 1
    display = 10  # 한 번에 가져올 아이템 수
    emotion = None
    pubDate = ''

    while cnt < srcCnt:
        jsonResponse = getNaverSearch(
            node, srcText, start, display, emotion, pubDate)  # [CODE 2]
        if jsonResponse['total'] > 0:
            for post in jsonResponse['items']:
                if 'naver' in post['link']:  # 'naver'가 포함된 'link'만 선택
                    full_text = get_full_article(post['link'])
                    if full_text:
                        # 모델을 사용하여 감정 분류
                        inputs = tokenizer(full_text, return_tensors="pt", max_length=512, truncation=True)
                        outputs = model(**inputs)
                        predicted_class = torch.argmax(outputs.logits).item()
                        
                        # 'label'을 기반으로 감정을 설정
                        if predicted_class == 1:
                            emotion = "긍정적인 감정"
                        else:
                            emotion = "부정적인 감정"
                        print(predicted_class)
                        
                        jsonResult.append({
                            'cnt': cnt,
                            'title': post['title'],
                            'description': post['description'],
                            'org_link': post['originallink'],
                            'link': post['link'],
                            'full_text': full_text,
                            'emotion': emotion,
                            'pub_date': post['pubDate']
                        })
                        cnt += 1
                        if cnt == srcCnt:
                            break
        else:
            print("더 이상 결과가 없습니다.")
            break
        start += display  # 다음 페이지로 이동

    print('전체 검색 : %d 건' % len(jsonResult))

    # with open('%s_naver_%s.json' % (srcText, node), 'w', encoding='utf8') as outfile:
    #     jsonFile = json.dumps(jsonResult, indent=4,
    #                           sort_keys=True, ensure_ascii=False)
    #     outfile.write(jsonFile)

    print("가져온 데이터 : %d 건" % (cnt))
    print('%s_naver_%s.json SAVED' % (srcText, node))

    return jsonResult