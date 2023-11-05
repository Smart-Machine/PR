import json
import time
import pika
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.http import Request


class RabbitMQ():
    def __init__(self, host, queue_name):
        self.host = host
        self.queue_name = queue_name

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host))
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue=queue_name)

    def publish_message(self, message):
        self.channel.basic_publish(
            exchange='', routing_key=self.queue_name, body=message)
        print(f" [x] Sent '{message}'")

    def end_connection(self):
        self.connection.close()


class CrawlSpider999(scrapy.Spider):
    name = "999_crawl"

    list_of_items = []
    query_link = "https://999.md/ro/list/real-estate/apartments-and-rooms?page={}"

    filename = "urls.txt"

    def start_requests(self, page_number="1", max_page_number=None):
        max_page_number = 10

        return [Request(
            url=self.query_link.format(page_number),
            callback=self.parse_links,
            dont_filter=True,
            meta={
                "request_id": time.time(),
                "page_number": page_number,
                "max_page_number": max_page_number,
            },
        )]

    def parse_links(self, response):
        items = response.xpath(
            "//*[contains(@class, 'ads-list-photo-item-title')]/a/@href").extract()
        self.list_of_items.append(items)

        if (response.meta.get("max_page_number") is not None and
                int(response.meta.get("page_number"))+1 > response.meta.get("max_page_number")):
            return self.get_links()

        if response.meta.get("page_number") in response.xpath("//nav[contains(@class, 'paginator cf')]/ul/li/a/text()").extract():
            return Request(
                url=self.query_link.format(
                    str(int(response.meta.get("page_number")) + 1)),
                callback=self.parse_links,
                dont_filter=True,
                meta={
                    **response.meta,
                    "page_number": str(int(response.meta.get("page_number")) + 1),
                },
            )

        return self.get_links()

    def get_links(self):
        clean_list = []
        for link_list in self.list_of_items:
            for link in link_list:
                if "/booster" not in link:
                    clean_list.append("https://999.md"+link)

        with open(self.filename, "w") as file:
            for link in clean_list:
                file.write(link + "\n")

        return self.get_items({"links": clean_list})

    def get_items(self, links):
        for link in links["links"]:
            yield Request(
                url=link,
                callback=self.parse_items,
                dont_filter=True,
            )

    def parse_items(self, response):
        return {
            "title": response.xpath("//header[contains(@class, 'adPage__header')]/h1/text()").extract_first(),
            "price": response.xpath("//span[contains(@class, 'adPage__content__price-feature__prices__price__value')]/text()").extract_first() + response.xpath("//span[contains(@class, 'adPage__content__price-feature__prices__price__currency')]/text()").extract_first(),
            "location": "".join(response.xpath("//dl[contains(@class, 'adPage__content__region')]/dd/text()").extract()),
            "description": response.xpath("//div[contains(@class, 'adPage__content__description')]/text()").extract_first(),
        }


class ItemCollectorPipeline():
    def process_item(self, item, spider):
        final_item = {}
        for key, value in item.items():
            final_item[key] = value.strip().replace("\n", " ")
        return final_item


class ItemPublisherPipeline():
    def open_spider(self, spider):
        self.rabbitmq = RabbitMQ("localhost", "scraper_queue")

    def close_spider(self, spider):
        self.rabbitmq.end_connection()

    def process_item(self, item, spider):
        self.rabbitmq.publish_message(
            json.dumps(item, indent=4, ensure_ascii=False))
        return item


if __name__ == "__main__":
    process = CrawlerProcess({
        "USER_AGENT": "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
        "ITEM_PIPELINES": {
            "__main__.ItemCollectorPipeline": 100,
            "__main__.ItemPublisherPipeline": 200,
        },
    })
    process.crawl(CrawlSpider999)
    process.start()
