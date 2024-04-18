import os
import urllib.request
import datetime
import json
import requests
from bs4 import BeautifulSoup
import json
import torch
import html

from transformers import AutoModelForSequenceClassification, AutoTokenizer

model_name = "jaehyeong/koelectra-base-v3-generalized-sentiment-analysis"
model = AutoModelForSequenceClassification.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

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
def getNaverSearch(node, srcText, start, display, emotion):
    base = "https://openapi.naver.com/v1/search"
    node = "/%s.json" % node
    parameters = "?query=%s&start=%s&display=%s&emotion=%s" % (
        urllib.parse.quote(srcText), start, display, urllib.parse.quote(str(emotion)))

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

# HTML 태그와 특수 문자 제거 함수
def clean_text(text):
    # BeautifulSoup를 사용하여 HTML 태그 제거
    soup = BeautifulSoup(text, 'html.parser')
    cleaned_text = soup.get_text(separator=' ', strip=True)
    
    # HTML 엔터티를 일반 문자로 변환
    cleaned_text = html.unescape(cleaned_text)
    
    return cleaned_text

# 수정된 함수
async def crawling(srcText: str, srcCnt: int):
    node = 'news'
    srcText = srcText
    cnt = 0
    jsonResult = []
    start = 1
    display = 10
    emotion = None

    while cnt < srcCnt:
        jsonResponse = getNaverSearch(node, srcText, start, display, emotion)
        if jsonResponse['total'] > 0:
            for post in jsonResponse['items']:
                if 'naver' in post['link']:
                    full_text = get_full_article(post['link'])
                    if full_text:
                        # clean_text 함수를 사용하여 title과 description 정제
                        cleaned_title = clean_text(post['title'])
                        cleaned_description = clean_text(post['description'])

                        inputs = tokenizer(full_text, return_tensors="pt", max_length=512, truncation=True)
                        outputs = model(**inputs)
                        predicted_class = torch.argmax(outputs.logits).item()
                        
                        if predicted_class == 1:
                            emotion = "pos_emo"
                        else:
                            emotion = "neg_emo"
                        print(predicted_class)
                        
                        # 감성 스코어 계산
                        score = torch.softmax(outputs.logits, dim=1)[0].tolist()
                        positive_score = score[1]
                        negative_score = score[0]
                        
                        # 날짜 포맷 변경
                        pub_date = datetime.datetime.strptime(post['pubDate'], "%a, %d %b %Y %H:%M:%S %z")
                        formatted_date = pub_date.strftime("%Y년 %m월 %d일 %A %H:%M")

                        jsonResult.append({
                            'cnt': cnt,
                            'title': cleaned_title,
                            'description': cleaned_description,
                            'org_link': post['originallink'],
                            'link': post['link'],
                            'full_text': full_text,
                            'emotion': emotion,
                            'positive_score': positive_score,
                            'postive_percent': round(float(positive_score) * 100),
                            'negative_score': negative_score,
                            'negative_percent': round(float(negative_score) * 100),
                            'pub_date': formatted_date
                        })
                        cnt += 1
                        if cnt == srcCnt:
                            break
        else:
            print("No more results.")
            break
        start += display

    print('Total search results: %d' % len(jsonResult))

    # 클라이언트 화면에 표시할 기사 수를 3개로 제한
    limitedResult = jsonResult[:3]  # 상위 3개 결과 선택

    print("Data to be displayed on the client: %d items" % (len(limitedResult)))
    print('%s_naver_%s.json SAVED' % (srcText, node))

    return limitedResult
