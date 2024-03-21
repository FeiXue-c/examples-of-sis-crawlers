# examples-of-sis-crawlers

一个简单的爬虫脚本用以从目标网站sis001抓取小说到本地

## novels.py:

&#x9;	本模块用于抓取特定分区的小说内容，并保存到本地。**目前仅初步完成抓取第一页所有内容并拼接保存到本地txt文件中。**==目前只能抓取第一页内容，自动翻页抓取功能开发中！==



*   已添加帖子在多页情况下自动翻页抓取内容到本地（由于忘记做字数过滤，所以会把所有评论一起抓进文本，先凑合着用吧）

环境依赖：

***

*   **jinja2**
*   **beautifulsoup**
*   **requests**

***

### **简易使用指南**

具体执行的脚本文件为[examples-of-sis-crawlers](https://github.com/FeiXue-c/examples-of-sis-crawlers/tree/main)/[novels](https://github.com/FeiXue-c/examples-of-sis-crawlers/tree/main/novels)/novels.py

```python
#需要手动配置的参数

# 需要抓取的页数，具体数值取决于需要抓取的分区
endPage = 105

# 起始页，默认从第一页开始抓取，无特殊需求不要改动
startPage = 1

# 对应分区的URL（示例为长篇收藏区）
baseUrl = 'http://104.194.212.35/forum/forum-334-%d.html'

# 网站当前IP，脚本启动前先确认下当前网站ip（不要用域名，大概率会出问题）
currentIP = '104.194.212.XX'

# 下载列表序号（由于小说过多，暂未实现多线程下载）(ps:我怕多线程下载会被ban)
dlPageNum = 1

# 是否开启顺序下载，开启后抓取完dlPageNum对应分页后自动取解析后续分页(目前逻辑为先按页抓取URL并存储到分页文件，再通过解析对应分页文件批量抓取小说内容)
dlSequentialSwitch = False
```

启动脚本后会自动生成Books和NovelsUrl文件夹，其中Books用于存储txt文件，NovelsUrl用于存储分页url

## 后续计划：没有后续计划，更新全看缘分,凑合着用得了