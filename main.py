import scrapy
from scrapy.crawler import CrawlerProcess
from full_autoria import FullAutoriaSpider

process = CrawlerProcess(settings={
    "FEEDS": {
        "items.json": {
            "format": "json",
            "indent": 4,
            'encoding': 'utf8',
        },
    },
})

process.crawl(FullAutoriaSpider)
process.start()
