"""
Problem Statement:

    - Implement a multithreaded web crawler starting from a given URL. You need to:
        - Crawl only URLs within the same domain.
        - Avoid revisiting the same URL.
        - Crawl in parallel using multiple threads.

    - Interface:
        class HtmlParser:
            def getUrls(self, url: str) -> List[str]:
                \"""
                Returns all urls linked from the given URL
                \"""
                pass
                
    - Function signature:
        def crawl(startUrl: str, htmlParser: 'HtmlParser') -> List[str]:
            pass

    - Constraints:
        - You need to ensure:
        - Thread-safe access to visited URLs
            - Efficient parallel crawling
            - Only crawl URLs that match the domain of startUrl

Approach:
    - Create mukltiple threads (3) to crawl all urls starting with startURL.
    - WebCrawler
        - urls_to_visit = [startURL]
        - visited_urls = []
        - access shared resource (urls_to_visit and visited_urls) using locks. (2 different locks ok.)
        - htmlParser (Access to parser object that returns urls inside startUrl)
        + crawl():
            - Access unvisited_url and visit with this thread.

Note:
    - Below doesn't check if url already visited -- need to improve check v2.
    - Also, only parse same domain name urls (This check is also not implemented.)
"""
import threading
import time
import random

class HtmlParser:
    def getUrls(self, url: str) -> list[str]:
        """
        Returns all urls linked from the given URL
        """
        time.sleep(2)
        random_count = random.randint(0, 1)
        urls = []
        for i in range(random_count):
            urls.append(url + str(i))
        return urls

class WebCrawler:
    def __init__(self):
        self.start_url = None
        self.urls_to_visit = []
        self.visited_urls = []
        self.visited_lock = threading.Lock()
        self.unvisited_lock = threading.Lock()
        self.htmlParser = HtmlParser()
        self.url_available = threading.Condition(self.unvisited_lock)

    def set_start_url(self, startURL):
        print(f"Setting start-url with: {startURL}")
        self.start_url = startURL

        with self.unvisited_lock:
            self.urls_to_visit.append(self.start_url)
    
    def crawl(self):
        while True:
            with self.unvisited_lock:
                while len(self.urls_to_visit) == 0:
                    print("No URLs to process. Waiting..")
                    self.url_available.wait(timeout=3)
                    if len(self.urls_to_visit) == 0:
                        return
                
                url_to_traverse = self.urls_to_visit.pop()

            # Append url to visited_urls, just for audit purpose.  
            print(f"Thread with id: {threading.get_ident()} processing {url_to_traverse}")
            with self.visited_lock:
                # TODO: Here we should have one more check if already visited no need to push, directly return.
                self.visited_urls.append(url_to_traverse)
            
            try:
                urls = self.htmlParser.getUrls(url_to_traverse)
                print("URLs found within current url: ", urls)
                with self.unvisited_lock:
                    self.urls_to_visit.extend(urls)
                    self.url_available.notify_all()
            except Exception as e:
                print(f"Unable to process url: {url_to_traverse} present in domain.")
            
            
# Set start url to a web crawler.
wc = WebCrawler()
wc.set_start_url("https://this-is-start-url/")

threads = [threading.Thread(target=wc.crawl) for _ in range(3)]

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()
