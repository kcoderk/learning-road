# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
from urllib import parse
from ArticleSpider.items import ArticleItem
import datetime

class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        '''
        获取文章列表url给下载器解析
        获取下一页url
        :param response:
        :return:
        '''
        # 获取列表URL和封面图片URL
        post_nodes = response.xpath('//div[@class="post floated-thumb"]//div[@class="post-thumb"]/a')
        for post_node in post_nodes:
            post_url = post_node.xpath('@href').extract_first("")
            img_url = post_node.xpath('img/@src').extract_first("")
            yield Request(url=parse.urljoin(response.url, post_url),
                          meta={'meta_img_url': parse.urljoin(response.url, img_url)}, callback=self.detail)
        # post_urls=response.xpath('//div[@class="post floated-thumb"]//div[@class="post-thumb"]/a/@href').extract()
        # for post_url in post_urls:
        #     yield Request(url=parse.urljoin(response.url,post_url),callback=self.detail)
        # 获取下一页URL
        next_page = response.xpath('//a[@class="next page-numbers"]/@href').extract_first()
        if next_page is not None:
            yield Request(url=parse.urljoin(response.url, next_page), callback=self.parse)
        else:
            return

    def detail(self, response):
        article_item = ArticleItem()
        # 标题
        title = response.xpath('//div[@class="entry-header"]/h1/text()').extract_first()
        # //*[@id=""]/div[1]/h1/text()
        # 发表日期
        create_date = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract_first().replace("·",
                                                                                                            "").strip()
        try:
            create_date=datetime.datetime.strptime(create_date,"%Y/%m/%d").date()
        except Exception as e:
            create_date=datetime.datetime.now().date()
        # 点赞数
        praise_nums = response.xpath('//div[@class="post-adds"]/span/h10/text()').extract_first()
        if praise_nums is not None:
            praise_nums=int(praise_nums.strip())
        else:
            praise_nums=0
        # 收藏数
        bookmark_nums = response.xpath(
            '//span[@class=" btn-bluet-bigger href-style bookmark-btn  register-user-only "]/text()').extract()[
            0].strip()
        bookmark_nums = re.match(".*?(\d+).*", bookmark_nums)
        if bookmark_nums:
            bookmark_nums = int(bookmark_nums.group(1))
        else:
            bookmark_nums = 0
        # 评论数获取
        comment_nums = response.xpath('//span[@class="btn-bluet-bigger href-style hide-on-480"]/text()').extract()[
            0].strip()
        comment_nums = re.match(".*?(\d+).*", comment_nums)
        if comment_nums:
            comment_nums = int(comment_nums.group(1))
        else:
            comment_nums = 0
        # 正文内容
        content = response.xpath('//div[@class="entry"]').xpath('string(.)').extract_first()
        # entry-meta-hide-on-mobile
        # 获取标签列表
        tags = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/a/text()').extract()
        tags = [element for element in tags if not element.strip().endswith("评论")]
        tags = ",".join(tags)
        # 封面图
        front_img = response.meta.get("meta_img_url", "")
        article_item["title"] = title
        article_item["url"] = response.url
        article_item["create_date"] = create_date
        article_item["praise_nums"] = int(praise_nums)
        article_item["bookmark_nums"] = bookmark_nums
        article_item["comment_nums"] = comment_nums
        article_item["content"] = content
        article_item["tags"] = tags
        article_item["img_url"] = [front_img]
        yield article_item
