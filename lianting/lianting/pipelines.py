# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from lianting.items import NovelItem, ChapterItem
from pymysql import cursors
from twisted.enterprise import adbapi
import copy
import logging


class LiantingPipeline:
    # 函数初始化
    def __init__(self, db_pool):
        self.db_pool = db_pool

    @classmethod
    def from_settings(cls, settings):
        """类方法，只加载一次，数据库初始化"""
        db_params = dict(
            host=settings['MYSQL_HOST'],
            user=settings['MYSQL_USER'],
            password=settings['MYSQL_PASSWORD'],
            port=settings['MYSQL_PORT'],
            database=settings['MYSQL_DBNAME'],
            charset=settings['MYSQL_CHARSET'],
            use_unicode=True,
            # 设置游标类型
            cursorclass=cursors.DictCursor
        )
        # 创建连接池
        db_pool = adbapi.ConnectionPool('pymysql', **db_params)
        # 返回一个pipeline对象
        return cls(db_pool)

    def process_item(self, item, spider):
        if isinstance(item, NovelItem):
            novelItem = {}
            novelItem['book_id'] = item['book_id']
            novelItem['name'] = item['name']
            novelItem['img'] = item['img']
            novelItem['tags'] = item['tags']
            novelItem['author'] = item['author']
            novelItem['audio_author'] = item['audio_author']
            novelItem['update_time'] = item['update_time']
            novelItem['intro'] = item['intro']
            novelItem['status'] = item['status']
            # 对象拷贝，深拷贝  --- 这里是解决数据重复问题！！！
            asynItem = copy.deepcopy(novelItem)
            # 把要执行的sql放入连接池
            query = self.db_pool.runInteraction(self.insert_novel_into, asynItem)

            # 如果sql执行发送错误,自动回调addErrBack()函数
            query.addErrback(self.handle_error, asynItem, spider)
        if isinstance(item, ChapterItem):
            chapterItem = {}
            chapterItem['book_id'] = item['book_id']
            chapterItem['order'] = item['order']
            chapterItem['title'] = item['title']
            chapterItem['url'] = item['url']
            # 对象拷贝，深拷贝  --- 这里是解决数据重复问题！！！
            asynItem = copy.deepcopy(chapterItem)
            # 把要执行的sql放入连接池
            query = self.db_pool.runInteraction(self.insert_chapter_into, asynItem)
            # 如果sql执行发送错误,自动回调addErrBack()函数
            query.addErrback(self.handle_error, asynItem, spider)
        return item

    # 处理sql函数
    def insert_novel_into(self, cursor, item):
        # 创建sql语句
        sql = "INSERT INTO novel (book_id,name,img,tags,author,audio_author,update_time,intro,status) " \
              "VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(
            item['book_id'], item['name'], item['img'], item['tags'], item['author'], item['audio_author'],
            item['update_time'], item['intro'], item['status'])
        # 执行sql语句
        logging.info(sql)
        cursor.execute(sql)

    # 处理sql函数
    def insert_chapter_into(self, cursor, item):
        # 创建sql语句
        sql = "INSERT INTO chapter (book_id,num,title,url) VALUES ('{}','{}','{}','{}')".format(
            item['book_id'], item['order'], item['title'], item['url'])
        logging.info(sql)
        # 执行sql语句
        cursor.execute(sql)

    # 错误函数
    def handle_error(self, failure, item, spider):
        # #输出错误信息
        print("failure", failure)