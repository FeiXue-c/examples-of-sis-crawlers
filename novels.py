#!/usr/bin/python
# coding=utf-8

import requests
import re
from bs4 import BeautifulSoup






def get_url_txt(url):
    print(url)
    r = requests.get(url)
    r.encoding = 'utf-8'
    html = r.text

    soup = BeautifulSoup(html, "html.parser")
    body = soup.form

    # 文章标题
    # 使用正则表达式匹配非UTF-8字符和一些常见的转义字符
    # 这里使用了Python的原始字符串(r前缀)来避免对反斜杠的额外转义
    pattern = r'[\x00-\x1F\x7F-\xFF]|[\x80-\xBF](?![\x80-\xBF])|(?<![\xC0-\xDF])[\x80-\xBF]'
    # 替换匹配到的字符为空格
    title = re.sub(pattern, ' ', body.h1.string)
    # 主贴内容
    div_tags = body.find_all("div", recursive=False)
    with open(title + ".txt", 'w', encoding='utf-8') as file:
        for div in div_tags:
            for content in div.find_all(attrs={"class": "t_msgfont noSelect"}):
                text_content = content.get_text(separator="\n", strip=True)
                file.write(text_content + "\n")


# 多进程提高方法执行速度
if __name__ == '__main__':
    # get_url_txt(url)单独调用时
    get_url_txt("http://104.194.212.35/forum/thread-11518015-1-1.html")

