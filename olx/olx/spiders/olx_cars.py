import scrapy
# from scrapy.utils.response import open_in_browser
from scrapy.utils.project import get_project_settings
import scraper_helper as helper
from ..items import OlxItem

from scrapy.spidermiddlewares.httperror import HttpError
from scrapy.exceptions import CloseSpider

settings = get_project_settings()

proxy_info = {
    "proxy": f"http://scraperapi:{settings.get('SCRAPER_API_KEY')}@proxy-server.scraperapi.com:8001"
}


class OlxCarsSpider(scrapy.Spider):
    name = 'olx_cars'
    allowed_domains = ['olx.com.br']
    urls = ['https://ma.olx.com.br/regiao-de-sao-luis/sao-luis/autos-e-pecas/carros-vans-e-utilitarios']

    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url, meta=proxy_info)

    def parse(self, response, **kwargs):
        # total_pages = 0  # Only Test
        total_pages = response.xpath('//p[contains(text(), "Página")]/text()[2]').get().split(' ')[2]
        if total_pages:
            for i in range(2, int(total_pages) + 1):
                url = helper.change_param(response.url, param='o', new_value=str(i), create_new=True)
                url = response.urljoin(url)
                yield scrapy.Request(url,
                                     callback=self.parse,
                                     meta=proxy_info,
                                     errback=self.handle_error)

        xp_base = '//ul[@id="ad-list"]/li//a[@data-lurker-detail="list_id"]'
        for result in response.xpath(xp_base):
            item = OlxItem()
            item['title'] = result.xpath('.//div[contains(@class, "fnmrjs-1")]/div[3]//h2/text()').get()
            item['price'] = result.xpath('.//div[contains(@class, "fnmrjs-1")]/div[3]//p/text()').get()
            item['link'] = result.xpath('.//@href').get()
            yield scrapy.Request(url=item['link'],
                                 callback=self.parse_details,
                                 meta=proxy_info,
                                 cb_kwargs={
                                     'item': item
                                 })

    def parse_details(self, response, item):
        imgs = []
        for result in response.xpath('//div[contains(@class, "gabobT")]/*[@data-testid="slides-wrapper"]//img'):
            imgs.append(result.xpath('.//@src').get())

        item['details'] = [{
            'imgs': imgs,
            'categoria': response.xpath('//*[contains(text(), "Categoria")]/following-sibling::a/text()').get(),
            'marca': response.xpath('//*[contains(text(), "Marca")]/following-sibling::a/text()').get(),
            'ano': response.xpath('//*[contains(text(), "Ano")]/following-sibling::a/text()').get(),
            'potencia_do_motor': response.xpath('//*[contains(text(), "Potência do '
                                                'motor")]/following-sibling::span/text()').get(),
            'cambio': response.xpath('//*[contains(text(), "Câmbio")]/following-sibling::span/text()').get()
        }]
        yield item

    def handle_error(self, failure):
        if failure.check(HttpError):
            response = failure.value.response
            if response.status == 429:  # Too Many Requests
                # open_in_browser(response)  # for debugging 429
                raise CloseSpider('Banned?')  # Comment out for proxies
