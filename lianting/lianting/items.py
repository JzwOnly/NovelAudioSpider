# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NovelItem(scrapy.Item):
    book_id = scrapy.Field()
    name = scrapy.Field()
    img = scrapy.Field()
    tags = scrapy.Field()
    author = scrapy.Field()
    audio_author = scrapy.Field()
    update_time = scrapy.Field()
    intro = scrapy.Field()
    # 0-未知 1-连载中 2-已完结
    status = scrapy.Field()


class ChapterItem(scrapy.Item):
    book_id = scrapy.Field()
    order = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()

