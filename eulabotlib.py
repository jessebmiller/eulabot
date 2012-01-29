import urllib
import re

DEFAULT_CRAWL_MAX = 10

def default_payload(page_str):
    pass

def default_url_handler(urls):
    pass

def get_page_str(url, domain):
    """ returns a string containing the resource at url on domain """

    page_str = urllib.urlopen('http://' + domain + '/' + url).read()
    return page_str

def all_links(page_str):
    """ returns a list of the links found in the given page string """
    
    matches = re.findall(' href=[\'"]([^\'"]+)[\'"]', page_str)
    return matches

class CrawlSet(object):
    """ a set of urls """

    def __init__(self, initial_cset=[]):
        self.cset = initial_cset

    def __len__(self):
        return len(self.cset)
        
    def __contains__(self, test_item):
        if test_item in self.cset:
            return True
        else: 
            return False

class CrawlQueue(CrawlSet):
    """ a set of urls we have yet to crawl """

    def dequeue(self):
        return self.cset.pop()

    def enqueue(self, item):
        self.cset.insert(0, item)
        return True


class DoNotCrawlList(CrawlSet):
    """ a set of urls we will not crawl """

    def add(self, item):
        self.cset.append(item)

class Spider(object):
    """ 
    keeps the crawl queue and do not crawl list updated as it loads and parses urls
    @TODO: describe a Spider better in this docstring ... damn

    with the current setup the spider cannot get out of the START_DOMAIN because there
    is no method for handling domains

    also with the current setup only relative links on the target page will work because we 
    assume the domain.

    @TODO handle domains intelegently. put a plan together to ensure that a spider will not 
    hit a domain to frequently. 
    """
    
    def __init__(self, \
                     domain, \
                     initial_crawl_urls, \
                     initial_no_crawl_urls, \
                     url_handler=default_url_handler, \
                     payload=default_payload, \
                     crawl_counter=DEFAULT_CRAWL_MAX):

        self.domain = domain
        self.crawl_queue = CrawlQueue(initial_crawl_urls)
        self.do_not_crawl_list = DoNotCrawlList(initial_no_crawl_urls)
        self.url_handler = url_handler
        self.payload = payload
        self.crawl_counter = crawl_counter

    def get_next_page_str(self):
        """ 
        returns the page string of the next url in the crawl queue
        """
        
        if self.crawl_counter < 1:
            return False

        this_url = self.crawl_queue.dequeue()
        if this_url not in self.do_not_crawl_list:
            self.do_not_crawl_list.add(this_url)
            self.crawl_counter -= 1
            
            return get_page_str(this_url, self.domain)
        
    def handle_urls(self, urls):
        """
        runs the url handler with the correct arguements
        """
        
        return self.url_handler(urls, self.do_not_crawl_list, self.crawl_queue)

    def run_payload(self, page_str):
        """
        runs the payload with correct arguements
        """
        
        return self.payload(page_str)
