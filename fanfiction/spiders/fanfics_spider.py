import scrapy
import re


class FanficsSpider(scrapy.Spider):
    name = "fanfics"
    start_urls = []

    # scrapy crawl fanfics -a url="https://m.fanfiction.net/book/Harry-Potter" -o fanfics.json
    def __init__(self, url=None, *args, **kwargs):
        super(FanficsSpider, self).__init__(*args, **kwargs)
        if url:
            self.start_urls = [url]

    def parse(self, response):
        base_url = response.url.split("/")[2]
        for block in response.css("div.bs"):
            url = block.css("a.pull-right").attrib.get("href")
            info = block.css("div > div ::text")[0].extract().split(", ")
            is_normal = info[4].startswith("words:")
            words = info[4] if is_normal else info[3]

            chars = block.css("div > div ::text").extract()[-1][2:]
            if chars[-1] == "]":
                chars = chars[:-1]

            pairs = re.findall(r"\[([^\]]+)", chars) 

            yield {
                "name": block.css("a:nth-of-type(2)::text").extract(),
                "url": "{}/s/{}".format(base_url, url[3:]) if url else "",
                "description": block.css("div.bs ::text")[6].extract()[3:],
                "words": words.replace("words: ", ""),
                "genres": info[2] if is_normal else "",
                "pairs": [pair.split(", ") for pair in pairs],
                "chars": list(set(chars.replace("[", "").replace("]", ",").split(", ")))
            }

        next_page = response.css("center > *")[-1].attrib.get("href")
        self.log("Next page: {}".format(next_page))

        if next_page:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)
