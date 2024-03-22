#!/usr/bin/python
# coding=utf-8

import multiprocessing
import os
import re
import time

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
# 下载结束序号(不包括)
dlEndPageNum = 81
# 是否开启顺序下载
dlSequentialSwitch = False
# 是否开启更新抓取列表(初次使用请置为True)
updateCrawlListSwitch = False


def check_directory(directory_path):
    # 检查目录是否存在，如果不存在则创建
    try:
        os.makedirs(directory_path, exist_ok=True)
        print(f"The directory {directory_path} has been created or already exists.")
    except OSError as e:
        print(f"An error occurred while creating the directory {directory_path}: {e}")


def format_filename(filename):
    # 使用正则表达式匹配非UTF-8字符和一些常见的转义字符
    # 这里使用了Python的原始字符串(r前缀)来避免对反斜杠的额外转义
    pattern = r'[\x00-\x1F\x3A\x3F\x2F\x2A\x22\x7F-\xFF]|[\x80-\xBF](?![\x80-\xBF])|(?<![\xC0-\xDF])[\x80-\xBF]|[<>]'
    # 替换匹配到的字符为空格
    res_filename = re.sub(pattern, ' ', filename)
    return res_filename


def clean_file(filename):
    with open('../Books/' + filename + ".txt", 'w', encoding='utf-8') as file:
        file.write(filename + '\n')
        print(f"文件 {'../Books/' + filename + ".txt"} 已清空")


def get_partition_url(pagenum, baseurl):
    base_url = baseurl

    for page in range(pagenum, pagenum + 10):
        info = []
        r = requests.get(base_url % page)
        r.encoding = 'utf-8'
        html = r.text

        soup = BeautifulSoup(html, "html.parser")

        for tbody in soup.find_all('tbody', attrs={'id': lambda value: 'normalthread' in value}):
            if tbody is not None:
                comments = tbody.find('strong')
                if comments is not None:
                    if comments.string.isdigit() and int(comments.string) >= 0:
                        span = tbody.find('span', attrs={'id': re.compile(r'^thread_\d+$')})
                        if span.a is not None:
                            href = 'http://' + currentIP + '/forum/' + span.a.get('href')
                            msg = span.a.string
                            info.append({'link': href, 'text': msg})

        # 创建 PackageLoader 实例，传入包名和模板目录
        loader = PackageLoader('novels', 'templates')
        # 创建 Environment 实例，并传入加载器
        env = Environment(loader=loader)
        # 从环境中获取模板
        template = env.get_template('sis.template')
        # 填充内容
        content = template.render(information=info)

        filename = '../NovelsUrl/sisNovels-%d.html'
        with open(filename % page, 'w', encoding='utf-8') as file:
            file.write(content + "\n")


def get_url_from_txt(x):
    html_file_path = '../NovelsUrl/sisNovels-%d.html'
    with open(html_file_path % x, 'r', encoding='utf-8') as file:
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
            filename = format_filename(filename)
            clean_file(filename)
            get_txt_by_url(href, filename)


def def_get_url_from_txt():
    html_file_path = '../NovelsUrl/sisNovels-default.html'
    with open(html_file_path, 'r', encoding='utf-8') as file:
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
            filename = format_filename(filename)
            clean_file(filename)
            get_txt_by_url(href, filename)


def organize_text_formatting(soup):
    # 提取所有的文本内容，保留换行和空格
    text = soup.get_text(strip=True, separator='\n')

    # 处理连续的<br>标签
    lines = text.split('\n')
    processed_lines = []
    consecutive_br = False
    for line in lines:
        if line.strip() == '<br>':
            if consecutive_br:
                processed_lines.append('')  # 添加一个空行，表示两个连续的<br>
            consecutive_br = True
        else:
            consecutive_br = False
            if line.strip():  # 如果行不为空，则添加到结果中
                processed_lines.append(line)

    # 将处理后的行合并回一个字符串
    processed_text = '\n'.join(processed_lines)
    return processed_text


def get_txt_by_url(url, title):
    # print(title+"||"+url)
    r = requests.get(url)
    r.encoding = 'utf-8'
    html = r.text

    soup = BeautifulSoup(html, "html.parser")
    body = soup.form

    # 主贴内容
    if body is not None:
        div_tags = body.find_all("div", recursive=False)
        with open('../Books/' + title + ".txt", 'a', encoding='utf-8') as file:
            for div in div_tags:
                for content in div.find_all(attrs={"class": "t_msgfont noSelect"}):
                    text_content = extract_and_process_text(content)
                    if len(text_content) > 100:
                        file.write(text_content + "\n")

        next_href = soup.find(attrs={"class": "pages_btns"}).find(attrs={"class": "next"})
        if next_href is not None:
            next_url = 'http://' + currentIP + '/forum/' + next_href.get('href')
            get_txt_by_url(next_url, title)
    else:
        print("error:" + title)
        with open('../Books/0failfile.txt', 'a', encoding='utf-8') as file:
            error_info = title + "\n" + url + "\n\n"
            file.write(error_info)


# 自定义函数来处理<br>标签，保留连续的换行符，移除孤立的换行符
def process_br_tags(text):
    # 使用正则表达式将<br>标签替换为换行符
    text_with_br = text.replace('<br>', '\n')
    # 使用splitlines()分割文本
    lines = text_with_br.splitlines()
    if not lines:  # 如果列表为空，则直接返回空字符串
        return ""
    processed_lines = [lines[0]]  # 如果列表不为空，始终保留第一行
    for line in lines[1:]:
        if line.strip() or not processed_lines[-1].strip():
            processed_lines.append(line)
    return '\n'.join(processed_lines)


# 提取并处理文本
def extract_and_process_text(soup):
    # 提取所有文本节点，包括<br>标签之间的文本
    text_nodes = soup.find_all(string=True, recursive=True)
    # 拼接所有文本节点，同时保留<br>标签
    raw_text = ''.join(text_nodes)
    # 处理<br>标签，保留连续的换行符，移除孤立的换行符
    processed_text = process_br_tags(raw_text)
    return processed_text.strip()

if __name__ == '__main__':
    processes = []
    # 检查环境
    check_directory('../Books')
    check_directory('../NovelsUrl')

    totalFile = int((endPage - startPage) / 10 + 1)
    # for debug
    # def_get_url_from_txt()

    if updateCrawlListSwitch:
        print("开始拉取链接")
        start_time = time.time()  # 记录开始时间
        # 多进程提高方法执行速度
        for fileNum in range(0, totalFile):
            p = multiprocessing.Process(target=get_partition_url, args=(startPage + fileNum * 10, baseUrl))
            processes.append(p)
            p.start()  # 启动子进程

        # 等待所有子进程结束
        for p in processes:
            p.join()

        end_time = time.time()  # 记录结束时间
        total_time = end_time - start_time
        print(f'All workers have finished. Total time taken: {total_time:.2f} seconds.')

    print("开始抓取文本")
    if dlSequentialSwitch:
        for i in range(dlPageNum, dlEndPageNum):
            print("开始第%d页抓取" % i)
            get_url_from_txt(i)
            print("已完成第%d页抓取" % i)
    else:
        get_url_from_txt(dlPageNum)
