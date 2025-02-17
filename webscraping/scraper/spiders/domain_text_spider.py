import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.crawler import CrawlerProcess
from urllib.parse import urlparse
from typing import Optional, Callable

class DomainTextSpider(scrapy.Spider):
    name = "domain_text_spider"

    # scrapy-playwright settings
    custom_settings = {
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",  
    }
    
    def __init__(self, start_url: str, 
                 item_callback: Optional[Callable] = None, 
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        parsed = urlparse(start_url)
        if not parsed.scheme:
            start_url = "http://" + start_url
            parsed = urlparse(start_url)
        
        self.start_urls = [start_url]
        self.allowed_domains = [parsed.netloc]
        self.link_extractor = LinkExtractor()
        self.visited_urls = set()
        self.item_callback = item_callback

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [
                        {"method": "wait_for_selector", "selector": "body"}
                    ],
                },
                callback=self.parse
            )
    
    def parse(self, response):
        if response.url in self.visited_urls:
            return
        self.visited_urls.add(response.url)

        # Extract and clean visible text
        text_elements = response.xpath('//body//text()[not(ancestor::script|ancestor::style)]').getall()
        cleaned_text = [text.strip() for text in text_elements if text.strip()]
        content = '\n'.join(cleaned_text)

        # Create data item
        item = {
            'url': response.url,
            'content': content
        }

        # Pass to callback 
        if self.item_callback:
            self.item_callback(item)

        for link in self.link_extractor.extract_links(response):
            if link.url not in self.visited_urls:
                yield scrapy.Request(
                    link.url,
                    meta={
                        "playwright": True,
                        "playwright_page_methods": [
                            {"method": "wait_for_selector", "selector": "body"}
                        ],
                    },
                    callback=self.parse
                )

class ScrapyManager:
    def __init__(self):
        self.process = CrawlerProcess()
        self.items = []

    def _item_handler(self, item):
        """Handler that stores items in memory"""
        self.items.append(item)

    def run_spider(self, start_url: str, item_callback: Optional[Callable] = None):
        """
        Start the spider with callback
        """
        callback = item_callback or self._item_handler
        self.process.crawl(
            DomainTextSpider,
            start_url=start_url,
            item_callback=callback
        )
        self.process.start()

class LLMContextManager:
    def __init__(self, scrapy_manager: ScrapyManager):
        self.scrapy_manager = scrapy_manager
        self.context = []
        
    def build_context(self, start_url: str):
        # Process items in real-time during scraping
        self.scrapy_manager.run_spider(
            start_url=start_url,
            item_callback=self._process_item
        )
    
    def _process_item(self, item):
        self._add_to_context(item)
        print(f"Added {item['url']} to LLM context")
    
    def _add_to_context(self, item):
        self.context.append(item['content'])
        
    def get_context(self):
        return '\n\n'.join(self.context)

# Usage example
if __name__ == "__main__":
    scrapy_manager = ScrapyManager()
    llm_manager = LLMContextManager(scrapy_manager)
    
    llm_manager.build_context("https://tentris.io")
    
    full_context = llm_manager.get_context()
    print(f"Total context length: {len(full_context)} characters")
    print(full_context)
