from scrapy.exporters import JsonItemExporter


class OlxPipeline(object):
    def __init__(self):
        self.fp = open("cars.json", 'wb')  # Open the json file in wb mode
        self.exporter = JsonItemExporter(self.fp, ensure_ascii=False, encoding='utf-8')
        self.exporter.start_exporting()

    def open_spider(self, spider):
        print("The crawler has started...")

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.fp.close()
        print("The crawler is over!")
