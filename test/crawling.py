import os
import sys
import urllib.request
import datetime
import time
import json
import requests
from bs4 import BeautifulSoup
import json
from summary_news import summary_news
import asyncio

client_id = "SJ3xMvTBxcs9DUafVWMw"
client_secret = "I54Gwgi6yE"

# [CODE 1]


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

# [CODE 2]


def getNaverSearch(node, srcText, start, display):
    base = "https://openapi.naver.com/v1/search"
    node = "/%s.json" % node
    parameters = "?query=%s&start=%s&display=%s" % (
        urllib.parse.quote(srcText), start, display)

    url = base + node + parameters
    responseDecode = getRequestUrl(url)  # [CODE 1]

    if (responseDecode == None):
        return None
    else:
        return json.loads(responseDecode)


# [CODE 3]
# def getPostData(post, jsonResult, cnt):
#     title = post['title']
#     description = post['description']
#     org_link = post['originallink']
#     link = post['link']

#     pDate = datetime.datetime.strptime(post['pubDate'], '%a, %d %b %Y %H:%M:%S +0900')
#     pDate = pDate.strftime('%Y-%m-%d %H:%M:%S')

#     jsonResult.append({'cnt': cnt, 'title': title, 'description': description,
#                        'org_link': org_link, 'link': org_link, 'pDate': pDate})
#     return

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

# [CODE 0]
# def main():
#     node = 'news'  # 크롤링 할 대상
#     srcText = input('검색어를 입력하세요: ')
#     cnt = 0
#     jsonResult = []

#     jsonResponse = getNaverSearch(node, srcText, 1, 10)  # [CODE 2]
#     total = jsonResponse['total']

#     while ((jsonResponse != None) and (jsonResponse['display'] != 0)):
#         for post in jsonResponse['items']:
#             cnt += 1
#             getPostData(post, jsonResult, cnt)  # [CODE 3]

#         start = jsonResponse['start'] + jsonResponse['display']
#         jsonResponse = getNaverSearch(node, srcText, start, 100)  # [CODE 2]

#     print('전체 검색 : %d 건' % total)

#     with open('%s_naver_%s.json' % (srcText, node), 'w', encoding='utf8') as outfile:
#         jsonFile = json.dumps(jsonResult, indent=4, sort_keys=True, ensure_ascii=False)

#         outfile.write(jsonFile)

#     print("가져온 데이터 : %d 건" % (cnt))
#     print('%s_naver_%s.json SAVED' % (srcText, node))


# def main():
#     node = 'news'  # 크롤링 할 대상
#     srcText = input('검색어를 입력하세요: ')
#     cnt = 0
#     jsonResult = []

#     jsonResponse = getNaverSearch(node, srcText, 1, 10)  # [CODE 2]
#     if jsonResponse['total'] > 0:
#         for post in jsonResponse['items']:
#             cnt += 1
#             full_text = get_full_article(post['link'])
#             jsonResult.append({
#                 'cnt': cnt,
#                 'title': post['title'],
#                 'description': post['description'],
#                 'org_link': post['originallink'],
#                 'link': post['link'],
#                 'full_text': full_text
#             })

#     print('전체 검색 : %d 건' % len(jsonResult))

#     with open('%s_naver_%s.json' % (srcText, node), 'w', encoding='utf8') as outfile:
#         jsonFile = json.dumps(jsonResult, indent=4, sort_keys=True, ensure_ascii=False)
#         outfile.write(jsonFile)

#     print("가져온 데이터 : %d 건" % (cnt))
#     print('%s_naver_%s.json SAVED' % (srcText, node))

def main():
    node = 'news'  # 크롤링 할 대상
    srcText = input('검색어를 입력하세요: ')
    cnt = 0
    jsonResult = []
    start = 1
    display = 10  # 한 번에 가져올 아이템 수

    while cnt < 3:
        jsonResponse = getNaverSearch(
            node, srcText, start, display)  # [CODE 2]
        if jsonResponse['total'] > 0:
            for post in jsonResponse['items']:
                if 'naver' in post['link']:  # 'naver'가 포함된 'link'만 선택
                    full_text = get_full_article(post['link'])
                    if full_text:
                        jsonResult.append({
                            'cnt': cnt,
                            'title': post['title'],
                            'description': post['description'],
                            'org_link': post['originallink'],
                            'link': post['link'],
                            'full_text': full_text
                        })
                        cnt += 1
                        if cnt == 3:  # 결과가 3개가 되면 반복 중단
                            break
        else:
            print("더 이상 결과가 없습니다.")
            break
        start += display  # 다음 페이지로 이동

    print('전체 검색 : %d 건' % len(jsonResult))

    with open('%s_naver_%s.json' % (srcText, node), 'w', encoding='utf8') as outfile:
        jsonFile = json.dumps(jsonResult, indent=4,
                              sort_keys=True, ensure_ascii=False)
        outfile.write(jsonFile)

    print("가져온 데이터 : %d 건" % (cnt))
    print('%s_naver_%s.json SAVED' % (srcText, node))

    newsChunk = json.dumps(full_text, ensure_ascii=False, indent=4)

    print(newsChunk)

    # 현재 실행 중인 이벤트 루프가 없으면 새로운 이벤트 루프를 얻음
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # 이미 실행 중인 이벤트 루프가 있다면 새로운 루프를 생성
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # 비동기 함수 실행 및 결과 얻기
    result = loop.run_until_complete(summary_news(newsChunk))

    print("\n\n\n")
    print("요약본")
    print(result)


if __name__ == '__main__':
    main()
