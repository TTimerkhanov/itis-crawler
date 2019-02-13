from __future__ import absolute_import

from bs4 import BeautifulSoup
from python_site.items import PageItem
from scrapy import Request
from scrapy.http import Response
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class PythonSiteSpider(CrawlSpider):
    name = 'python_site'
    allowed_domains = ["python-course.eu"]
    start_urls = ['https://www.python-course.eu/']

    invalid_urls = []

    # This spider has one rule: extract all (unique) links,
    # follow them and parse them using the parse_items method
    rules = [
        Rule(
            LxmlLinkExtractor(
                unique=True,
            ),
            follow=True,

            callback="parse_items",
        )
    ]

    # Method which starts the requests by visiting all URLs specified in start_urls
    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, callback=self.parse, dont_filter=True)

    def clean_body(self, html):
        soup = BeautifulSoup(html)
        # Remove all javascript and stylesheet code
        for script in soup(["script", "style"]):
            script.extract()

        # Remove header
        header = soup.find(id='navlist')
        _ = header.extract()

        # Get text
        text = soup.get_text()

        # Break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        # Drop new line signs
        text = text.replace('\n', ' ')
        return text

    # Method for parsing items
    def parse_items(self, response: Response):
        # The list of items that are found on the particular page
        items = []
        # Only extract unique links (with respect to the current page)
        links = LxmlLinkExtractor(unique=True).extract_links(response)
        # Now go through all the found links
        for link in links:
            # Check whether the domain of the URL of the link is allowed;
            # so whether it is in one of the allowed domains
            is_allowed = False
            for allowed_domain in self.allowed_domains:
                if allowed_domain in link.url:
                    is_allowed = True

            # If it is allowed, create a new item and add it to the list of found items
            if is_allowed:
                # 404 error, populate the broken links array
                if response.status == 404:
                    self.invalid_urls.append({'url': response.url})
                else:
                    item = PageItem()
                    item['url'] = response.url

                    text = self.clean_body(response.body)
                    item['text'] = text
                    items.append(item)

        # Return all the found items
        return items
