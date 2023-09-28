import time
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.http import Request


class CrawlSpider999(scrapy.Spider):
    name = "999_crawl"

    list_of_items = []
    query_link = "https://999.md/ro/list/real-estate/apartments-and-rooms?page={}"

    def start_requests(self, page_number="1", max_page_number=None):
        max_page_number = 10

        return [Request(
            url=self.query_link.format(page_number),
            callback=self.parse_item,
            dont_filter=True,
            meta={
                "request_id": time.time(),
                "page_number": page_number,
                "max_page_number": max_page_number,
            },
        )]

    def parse_item(self, response):
        items = response.xpath(
            "//*[contains(@class, 'ads-list-photo-item-title')]/a/@href").extract()
        self.list_of_items.append(items)

        if (response.meta.get("max_page_number") is not None and 
            int(response.meta.get("page_number"))+1 > response.meta.get("max_page_number")):
            return self.get_items()

        if response.meta.get("page_number") in response.xpath("//nav[contains(@class, 'paginator cf')]/ul/li/a/text()").extract():
            return Request(
                url=self.query_link.format(
                    str(int(response.meta.get("page_number")) + 1)),
                callback=self.parse_item,
                dont_filter=True,
                meta={
                    **response.meta,
                    "page_number": str(int(response.meta.get("page_number")) + 1),
                },
            )

        return self.get_items()

    def get_items(self):
        clean_list = []
        for link_list in self.list_of_items:
            for link in link_list:
                if "/booster" not in link:
                    clean_list.append("https://999.md"+link)
        return {"links": clean_list}

    def see_response(self, response):
        from scrapy.shell import inspect_response
        inspect_response(response, self)
        return


if __name__ == "__main__":
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })

    process.crawl(CrawlSpider999)
    process.start()
