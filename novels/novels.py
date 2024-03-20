#!/usr/bin/python
# coding=utf-8

import multiprocessing
import os
import re

import requests
from bs4 import BeautifulSoup
from jinja2 import Environment, PackageLoader

# 目前只能抓取第一页内容，自动翻页抓取功能开发中

# 需要抓取的页数
endPage = 105
# 每个文件包含的几页的内容
startPage = 1
# 对应分区的URL
baseUrl = 'http://104.194.212.35/forum/forum-334-%d.html'
# 网站当前IP
currentIP = '104.194.212.35'
# 下载列表序号（由于小说过多，暂未实现多线程下载）
dlPageNum = 1
# 是否开启顺序下载
dlSequentialSwitch = False

# URL更新进度标志(勿动)
update_flag = 0


def check_directory(directory_path):
    # 检查目录是否存在，如果不存在则创建
    try:
        os.makedirs(directory_path, exist_ok=True)
        print(f"The directory {directory_path} has been created or already exists.")
    except OSError as e:
        print(f"An error occurred while creating the directory {directory_path}: {e}")


def get_partition_url(pagenum, baseurl):
    global update_flag
    base_url = baseurl
    info = []
    for i in range(pagenum, pagenum + 10):
        r = requests.get(base_url % i)
        r.encoding = 'utf-8'
        html = r.text

        soup = BeautifulSoup(html, "html.parser")
        for line in soup.find_all(id=re.compile("^normalthread")):
            if line is not None:
                comments = line.find('strong')
                if comments is not None:
                    if comments.string.isdigit() and int(comments.string) >= 0:
                        span = line.find(id=re.compile("^thread"))
                        if not span.contents[0].string:
                            continue
                        info.append({'link': 'http://' + currentIP + '/forum/' + span.contents[0].get('href'),
                                     'text': span.contents[0].string})

        # 创建 PackageLoader 实例，传入包名和模板目录
        loader = PackageLoader('novels', 'templates')
        # 创建 Environment 实例，并传入加载器
        env = Environment(loader=loader)
        # 从环境中获取模板
        template = env.get_template('sis.template')
        # 填充内容
        content = template.render(information=info)

        filename = '../NovelsUrl/sisNovels-%d.html'
        with open(filename % i, 'w', encoding='utf-8') as file:
            file.write(content + "\n")
    update_flag = update_flag + 1


def get_url_from_txt(x):
    print("Under development")
    html_file_path = '../NovelsUrl/sisNovels-%d.html'
    with open(html_file_path % (x + 1), 'r', encoding='utf-8') as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    # 查找所有的<a>标签
    links = soup.find_all('a')
    print(len(links))
    # 遍历所有<a>标签，并打印出href属性的值
    for link in links:
        href = link.get('href')
        filename = link.string
        if href:
            print(href)
            get_txt_by_url(href, filename)


def get_txt_by_url(url, name):
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
    title = re.sub(pattern, ' ', name)
    print(title)
    # 主贴内容
    div_tags = body.find_all("div", recursive=False)
    with open('../Books/' + title + ".txt", 'w', encoding='utf-8') as file:
        for div in div_tags:
            for content in div.find_all(attrs={"class": "t_msgfont noSelect"}):
                text_content = content.get_text(separator="\n", strip=True)
                file.write(text_content + "\n")



if __name__ == '__main__':

    # 检查环境
    check_directory('../Books')
    check_directory('../NovelsUrl')

    totalFile = int((endPage - startPage) / 10 + 1)

    # 多进程提高方法执行速度
    for fileNum in range(0, totalFile):
        multiprocessing.Process(target=get_partition_url, args=(startPage + fileNum * 10, baseUrl)).start()

    while update_flag == totalFile - 1:
        continue

    if dlSequentialSwitch:
        for fileNum in range(dlPageNum, endPage + 1):
            get_url_from_txt(fileNum)
    else:
        get_url_from_txt(dlPageNum)
