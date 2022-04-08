

import scrapy


class OlxItem(scrapy.Item):
    title = scrapy.Field()
    price = scrapy.Field()
    link = scrapy.Field()
    details = scrapy.Field()

