#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：NovelAudio
@File    ：lianting_spider.py
@IDE     ：PyCharm
@Author  ：jzw
@Date    ：2021/2/26 10:56 上午
"""
import scrapy
from bs4 import BeautifulSoup
import re
from scrapy.http import Request, FormRequest
from lianting.items import NovelItem, ChapterItem
import logging
import json
from urllib.parse import unquote


class liantingSpider(scrapy.Spider):
    name = "lianting"
    allowed_domains = ["m.ting55.com"]
    start_urls = [
        "https://m.ting55.com"
    ]
    web_domain = "https://m.ting55.com"

    def parse(self, response, **kwargs):
        soup = BeautifulSoup(response.text, 'lxml')  # 使用lxml则速度更快
        # 获取所有类别
        tags_list_html = soup.find('nav', {'class': 'nav clear'})\
            .findAll('a', {'href': re.compile(r'^/category/\d+')})
        tags_list = [{"tag_url": "{0}{1}".format(self.web_domain, tags_html.get(
            'href')), "tag_name": tags_html.text} for tags_html in tags_list_html]
        for tag in tags_list:
            meta_tag_novel = {
                'current_page': 1,
                'tag_name': tag["tag_name"],
                'tag_url': tag["tag_url"]
            }
            yield Request(url=tag["tag_url"], callback=self.parse_tag_novel_list, meta=meta_tag_novel)

    def parse_tag_novel_list(self, response):
        current_page = response.meta['current_page']
        tag_name = response.meta['tag_name']
        logging.info('开始爬取类型：{0}下，第{1}页的小说'.format(tag_name, current_page))
        soup = BeautifulSoup(response.text, 'lxml')  # 使用lxml则速度更快
        # 获取该类型下的小说列表
        novel_list_html = soup.find('div', {'class': 'clist'}).findAll('a')
        novel_list = [{"novel_url": "{0}{1}".format(self.web_domain, novel_html.get(
            'href')), "novel_name": novel_html.find('dd').find('h3').text} for novel_html in novel_list_html]
        for novel in novel_list:
            meta_novel = {
                'novel_name': novel["novel_name"],
                'novel_url': novel["novel_url"],
                'novel_tag': tag_name,
            }
            yield Request(url=novel["novel_url"], callback=self.parse_novel, meta=meta_novel)

        if current_page == 1:
            max_pages = re.match(r'页次.*?\d/(\d+)',
                                 soup.find('div',
                                           {'class': 'cpage'}).find('span').text).groups()[0]
            if int(max_pages) > 1:
                meta = response.meta
                meta['current_page'] = current_page + 1
                meta['max_pages'] = max_pages
                yield Request(url="{0}/page/{1}".format(meta["tag_url"], meta["current_page"]),
                              callback=self.parse_tag_novel_list, meta=meta)
        else:
            max_pages = response.meta['max_pages']
            if current_page <= max_pages:
                meta = response.meta
                meta['current_page'] = current_page + 1
                yield Request(url="{0}/page/{1}".format(meta["tag_url"], meta["current_page"]),
                              callback=self.parse_tag_novel_list, meta=meta)

    def parse_novel(self, response):
        novel_name = response.meta["novel_name"]
        logging.info('开始爬取小说：{0}'.format(novel_name))
        soup = BeautifulSoup(response.text, 'lxml')  # 使用lxml则速度更快
        # 获取小说信息
        novel_html = soup.find('div', {'class': 'book'})
        novel_id = re.match(r'https://m.ting55.com/book/(\d+)', response.meta["novel_url"]).groups()[0]
        novel_img = 'https:{0}'.format(novel_html.find(
            'div', {'class': 'bimg'}).find('img').get('src'))
        novel_info_html = novel_html.find(
            'div', {'class': 'binfo'}).findAll('p')
        novel_intro_list_html = soup.find(
            'div', {'class': 'intro'}).findAll('p')
        novel_intro = "\n".join(
            [novel_intro_html.text for novel_intro_html in novel_intro_list_html])
        novel_tag = response.meta["novel_tag"]
        novel_author = '未知'
        novel_audio_author = '未知'
        novel_update_time = '未知'
        novel_status = '0'
        for novel_info in novel_info_html:
            tag_result = re.match(r'类型：(.*?)', novel_info.text)
            author_result = re.match(r'作者：(.*?)', novel_info.text)
            audio_author_result = re.match(
                r'播音：(.*?)', novel_info.text)
            update_time_result = re.match(
                r'时间：(.*?)', novel_info.text)
            status_result = re.match(r'状态：(.*?)', novel_info.text)
            # 类型
            if tag_result:
                novel_tag = tag_result.groups()[0]
            if author_result:
                novel_author = author_result.groups()[0]
            if audio_author_result:
                audio_author_list_html = novel_info.findAll(
                    'span', {'class': 'bys'})
                audio_author_list_html2 = novel_info.findAll(
                    'a', {'class': 'by'})
                audio_author_total = ''
                if audio_author_list_html and len(audio_author_list_html) > 0:
                    audio_author = [
                        audio_author_html.text for audio_author_html in audio_author_list_html]
                    novel_audio_author = "{0},{1}".format(
                        audio_author_total, ",".join(audio_author))
                if audio_author_list_html2 and len(
                        audio_author_list_html2) > 0:
                    audio_author2 = [
                        audio_author_html2.text for audio_author_html2 in audio_author_list_html2]
                    novel_audio_author = "{0},{1}".format(
                        audio_author_total, ",".join(audio_author2))
            if update_time_result:
                novel_update_time = update_time_result.groups()[0]
            if status_result:
                if status_result.groups()[0] == '连载中':
                    novel_status = '1'
                elif status_result.groups()[0] == '全集完结':
                    novel_status = '2'

        # NovelItem() 封装
        novel_model = NovelItem()
        novel_model["book_id"] = novel_id
        novel_model["name"] = novel_name
        novel_model["img"] = novel_img
        novel_model["tags"] = novel_tag
        novel_model["author"] = novel_author
        novel_model["audio_author"] = novel_audio_author
        novel_model["update_time"] = novel_update_time
        novel_model["intro"] = novel_intro
        novel_model["status"] = novel_status
        yield novel_model

        play_list_html = soup.find('section', {'class': 'bookinfo'}).find('div', {'class': 'plist'})\
            .findAll('a', {'class': 'f'})
        play_list = ["{0}{1}".format(self.web_domain, play_html.get('href')) for play_html in play_list_html]
        for play_url in play_list:
            audio_meta = response.meta
            audio_meta['audio_url'] = play_url
            yield Request(url=play_url, callback=self.get_novel_audio, meta=audio_meta)

    def get_novel_audio(self, response):
        novel_name = response.meta["novel_name"]
        chapter = re.match(r'https://m.ting55.com/book/\d+-(\d+)', response.meta["audio_url"]).groups()[0]
        logging.info('开始爬取小说：{0} 第{1}章'.format(novel_name, chapter))
        soup = BeautifulSoup(response.text, 'lxml')  # 使用lxml则速度更快
        bsy_script = soup.find('script', {'src': '//img.ting55.com/site/m/bsy.js'})
        bxi_script = soup.find('script', {'src': '//img.ting55.com/site/m/bxi.js'})
        if bsy_script and bxi_script is None:
            path = '/mlink'
        elif bxi_script and bsy_script is None:
            path = '/glink'
        else:
            path = '/glink'
        headers = {'xt': soup.find('meta', {'name': '_c'}).get('content')}
        is_pay = soup.find('meta', {'name': '_p'}).get('content')
        page = soup.find('meta', {'name': '_cp'}).get('content')
        book_id = soup.find('meta', {'name': '_b'}).get('content')
        url = "{0}{1}".format(self.web_domain, path)
        data = {
            'bookId': book_id,
            'isPay': is_pay,
            'page': page
        }
        audio_meta = {
            'bookId': book_id,
            'order': page
        }
        yield FormRequest(url=url, headers=headers, formdata=data, callback=self.get_novel_audio_url, meta=audio_meta)

    @staticmethod
    def get_novel_audio_url(response):
        res = json.loads(response.text)
        if res['status'] == 1:
            chapter = ChapterItem()
            chapter["book_id"] = response.meta['bookId']
            chapter["title"] = unquote(res['title'], 'utf-8')
            chapter["url"] = res['ourl']
            chapter["order"] = response.meta['order']
            yield chapter
        else:
            logging.error('获取音频接口返回status!=1')
