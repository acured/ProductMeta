#from django.shortcuts import render
from rest_framework.response import Response
import requests
import json
from rest_framework import status
from openai import AzureOpenAI
from urllib3 import request
import os
from requests_html import HTMLSession
import time
import random

# Configuration
API_KEY = ""    # change to your API KEY
ENDPOINT = ""   # change to your Azure endpoint
PHOTO_API = ""  # change to your pexel.com API KEY


# 创建一个 HTML 会话
session = HTMLSession()

# 设置请求头以模拟浏览器
headers = {
    "Authorization": PHOTO_API,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

t = random.randint(0,12)
print(t)
time.sleep(t)

# 发送 GET 请求
response = session.get("https://api.pexels.com/v1/search?query=clock&per_page=3", headers=headers)

# 检查响应状态码
if response.status_code == 200:
    # 解析响应的JSON数据
    data = response.json()
    print(data)
    # 获取照片列表
    photos = data.get("photos", [])

    # 如果有照片，返回第一张照片的URL
    if photos:
        i = random.randint(0,len(photos)-1)
        photo_url = photos[i].get("src", {}).get("original", None)
        print(f"Found photo URL: {photo_url}")
    else:
        print("No photos found for the given keyword.")
else:
    print(f"Failed to fetch photos. Status code: {response.status_code}")
    print(f"Response content: {response.text}")



