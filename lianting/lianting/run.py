#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：NovelAudio 
@File    ：run.py
@IDE     ：PyCharm 
@Author  ：jzw
@Date    ：2021/3/3 9:56 上午 
"""
from scrapy import cmdline

cmdline.execute(['scrapy', 'crawl', 'lianting'])