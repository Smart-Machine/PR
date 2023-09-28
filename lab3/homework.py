import json
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.http import Request

FILENAME = "data.json"
ITEM_LIST = []


# Scraper class, where the links are crawled and data is extracted
class Homework(scrapy.Spider):
    name = "homework"
    urls = ["https://999.md/ro/83438035", "https://999.md/ro/84339856"]

    # Entry point, where the links are crawled
    def start_requests(self):
        for url in self.urls:
            yield Request(
                url=url,
                callback=self.parse_item,
                dont_filter=True,
            )

    # The function that extracts the product details 
    def parse_item(self, response):
        item = {
            "title": response.xpath("//header[contains(@class, 'adPage__header')]/h1/text()").extract_first(),
            "price": response.xpath("//span[contains(@class, 'adPage__content__price-feature__prices__price__value')]/text()").extract_first() + response.xpath("//span[contains(@class, 'adPage__content__price-feature__prices__price__currency')]/text()").extract_first(),
            "location": "".join(response.xpath("//dl[contains(@class, 'adPage__content__region')]/dd/text()").extract()),
            "description": response.xpath("//div[contains(@class, 'adPage__content__description')]/text()").extract_first(),
        }
        return item

# The pipeline class which processes the items, by cleaning the data
# and forwarding it into the desired queue (ITEM_LIST)
class ItemCollectorPipeline():
    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        final_item = {}
        for key, value in item.items():
            final_item[key] = value.strip().replace("\n", " ")
        ITEM_LIST.append(final_item)

# The entry point of the script
if __name__ == "__main__":
    # The Spider's Runner instance, with params
    process = CrawlerProcess({
        "USER_AGENT": "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
        "ITEM_PIPELINES": {'__main__.ItemCollectorPipeline': 100},
    })
    process.crawl(Homework)
    process.start()

    # Writing the scraped and processed items to the desired file
    with open(FILENAME, "w") as file:
        file.write(json.dumps(ITEM_LIST, indent=4, ensure_ascii=False))
