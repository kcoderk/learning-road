# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
import MySQLdb
class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


class ImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):#获取图片path
        for ok ,path in results:
            images_path=path['path']
        item['img_path']=images_path
        return item
class MysqlPipeline(object):
    def __init__(self):
        self.conn=MySQLdb.connect('localhost','root','root','jobbole',charset='utf8',use_unicode=True)
        self.cursor=self.conn.cursor()
    def process_item(self, item, spider):
        sql1='''
        insert into table2(title,img_url,create_date,url ,content,tags,img_path,comment_nums,praise_nums,bookmark_nums ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        '''#,item['img_url']
        self.cursor.execute(sql1,(item['title'],item['img_url'][0],item['create_date'],item['url'],item['content'],item['tags'],item['img_path'],item['comment_nums'],item['praise_nums'],item['bookmark_nums']))
        self.conn.commit()
        return item