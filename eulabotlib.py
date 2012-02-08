import urllib
import re

DEFAULT_CRAWL_MAX = 10

def default_payload(page_str):
    if page_str:
        print "default payload ran for:", page_str[:50], '...'
    else:
        print "there was no page string"

def default_url_handler(urls, do_not_crawl_list, crawl_queue):
    for url in urls:
        if url not in do_not_crawl_list:
            crawl_queue.enqueue(url)
            

def get_page_str(url, domain):
    """ returns a string containing the resource at url on domain """

    page_str = urllib.urlopen('http://' + domain + '/' + url).read()
    return page_str

def all_links(page_str):
    """ returns a list of the links found in the given page string """
    
    try: 
        matches = re.findall(' href=[\'"]([^\'"]+)[\'"]', page_str)
        return matches
    except:
        return None

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

    a eulabot spider is restricted to a single domain. We will create a spider for each domain
    
    this allows us to control the frequency by which we access a domain from within the spider object

    this does mean we will need a good way for spiders to exchange urls when they find urls for a domain 
    they are not allowed to access 

    a DB or dict external to the spider class seems appropriate
    """
    
    def __init__(self, \
                     domain, \
                     initial_crawl_urls, \
                     initial_no_crawl_urls, \
                     url_handler=default_url_handler, \
                     payload=default_payload, \
                     crawl_counter=DEFAULT_CRAWL_MAX, \
                     payload_args={}):

        self.domain = domain
        self.crawl_queue = CrawlQueue(initial_crawl_urls)
        self.do_not_crawl_list = DoNotCrawlList(initial_no_crawl_urls)
        self.url_handler = url_handler
        self.payload = payload
        self.crawl_counter = crawl_counter
        self.payload_args = payload_args
        self.results = []

    def get_next_page_str(self):
        """ 
        returns the page string of the next url in the crawl queue

        @TODO: This should probably not be doing as much of this here. 

        there might be a use for a get_page_str method
        but the crawl() method should be figuring out which url is next and should be in charge of the crawl queue
        """
        
        if self.crawl_counter < 1:
            return False

        if len(self.crawl_queue) > 0:
            
            while True:
                this_url = self.crawl_queue.dequeue()
                if this_url not in self.do_not_crawl_list:
                    break
                else:
                    print "whats %s doing in do not crawl and crawl queue?" % this_url
        
            if this_url not in self.do_not_crawl_list:
                self.do_not_crawl_list.add(this_url)
                self.crawl_counter -= 1
                page_str = get_page_str(this_url, self.domain)
                return page_str
            else: #url is in do_not_crawl
                return False
        else: 
            self.crawl_counter = 0
            
    def handle_urls(self, urls):
        """
        runs the url handler with the correct arguements
        """
        
        if urls:
            return self.url_handler(urls, self.do_not_crawl_list, self.crawl_queue)
        else:
            return None

    def run_payload(self, kwargs):
        """
        runs the payload with correct arguements
        """

        return self.payload(**kwargs)

    def crawl(self):
        """
        runs the crawl loop until we cannot go any further. Either because we ran out of our crawl counter, or we run out of the crawl queue.
        """
        
        while self.crawl_counter > 0 and len(self.crawl_queue) > 0:
            # load next page
            page_str = self.get_next_page_str()

            # get the links
            urls = all_links(page_str)
            
            # handle the links and run payload
            self.handle_urls(urls)
            
            self.payload_args.update({'page_str': page_str})
            result = self.run_payload(self.payload_args)
            if result: self.results.append(result)
            
        return self.results
