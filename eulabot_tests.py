from eulabotlib import *
import unittest
import hashlib
import re

def test_payload(page_str):
    """ 
    eventually we will need to use a database record to ensure this is running 

    for now we will just manually check that this thing printed
    """
    return 'ran_test_payload'

def test_url_handler(urls, do_not_crawl_list, crawl_queue):
    """ 
    adds 'test_no_crawl_url' to the do not crawl list 
    adds urls, to the crawl_que unless in do not crawl
    """

    do_not_crawl_list.add('test_no_crawl_url')
    
    for url in urls:
        if url not in do_not_crawl_list:
            crawl_queue.enqueue(url)
    
def test_crawl_payload(page_str):
    """ 
    hashes a concatination of the page string and the cumulative hash to verify that the 
    expected crawl occured
    """

    return hashlib.sha1(page_str).hexdigest()

class TestEulabot(unittest.TestCase):
    
    def setUp(self):
        self.test_domain = 'localhost:8000'
        self.crawl_counter = 10
        self.crawl_queue = CrawlQueue(['third', 'second', 'first'])
        self.do_not_crawl = DoNotCrawlList()
        self.spider = Spider(self.test_domain, \
                                 ['3', '2', 'test/get_page/'], \
                                 ['NOa', 'NOb', 'NOc'], \
                                 test_url_handler, \
                                 test_payload , \
                                 self.crawl_counter )


    def test_crawl(self):
        """
        makes sure that the crawl loop runs in order and does not break crawl rules
        """
        
        crawl_test_spider = Spider(self.test_domain+'/test/crawl_test', \
                                       ['1'], \
                                       [], \
                                       test_url_handler, \
                                       test_crawl_payload, \
                                       self.crawl_counter )

        crawl_test_spider2 = Spider(self.test_domain+'/test/crawl_test', \
                                       ['1'], \
                                       [], \
                                       test_url_handler, \
                                       test_crawl_payload, \
                                       self.crawl_counter )

        first_crawl_results = crawl_test_spider.crawl()
        second_crawl_results = crawl_test_spider2.crawl()
        
        self.assertEqual(len(first_crawl_results), self.crawl_counter)
        self.assertEqual(first_crawl_results, second_crawl_results)

    def test_spider_get_next_page_str(self):
        """
        ensures that the spider can perform the correct sequence
        
        get the next page (make sure it makes it into the do not crawl list)
        get the urls on the page
        run test_url_handler (make sure the do not crawl list is updated)
        run test_payload
        """

        self.assertEqual(self.spider.get_next_page_str(), 'pass')
        self.assertEqual(len(self.spider.crawl_queue), 2)
        self.assertTrue('test/get_page/' in self.spider.do_not_crawl_list)

        random_page_str = get_page_str('randopage', self.test_domain)
        urls = all_links(random_page_str)
        self.spider.handle_urls(urls)
        self.assertTrue('test_no_crawl_url' in self.spider.do_not_crawl_list)
        self.assertTrue(len(self.spider.crawl_queue) > 2)

        self.assertEqual(self.spider.run_payload({'page_str': random_page_str}), 'ran_test_payload')

    def test_spider_obeys_crawl_counter(self):
        counter_test_spider = Spider(self.test_domain, \
                                         ['3', '2', 'test/get_page/'], \
                                         ['NOa', 'NOb', 'NOc'], \
                                         test_url_handler, \
                                         test_payload, \
                                         2 )

        self.assertTrue(counter_test_spider.get_next_page_str())
        self.assertTrue(counter_test_spider.get_next_page_str())
        self.assertFalse(counter_test_spider.get_next_page_str())

    def test_spider_init(self):
        """ 
        ensures that a spider is created with all the appropriate pieces

        a working CrawlQueue with the initial given list of urls
        a working DoNotCrawlList
        contains a crawl counter
        contains a payload (a function that operates on the page string)
        contains a url handler (logic that decides which urls go in the do not crawl list/queue)
        """

        self.assertEqual(type(self.spider.crawl_queue), type(CrawlQueue())) 
        self.assertEqual(type(self.spider.do_not_crawl_list), type(DoNotCrawlList())) 
        self.assertEqual(type(self.spider.url_handler), type(test_payload)) 
        self.assertEqual(type(self.spider.payload), type(test_payload)) 
        self.assertTrue(self.spider.crawl_counter > 0)

    def test_do_not_crawl_add(self):
        self.do_not_crawl.add('dont crawl me')
        self.assertTrue('dont crawl me' in self.do_not_crawl)

    def test_crawl_queue_enqueue(self):
        self.crawl_queue.enqueue('queued')
        self.assertTrue( 'queued' in self.crawl_queue )

    def test_ger_crawl_queue_dequeue(self):
        self.crawl_queue.enqueue('fourth')
        self.assertEqual( self.crawl_queue.dequeue(), 'first' )
        self.assertEqual( self.crawl_queue.dequeue(), 'second' )
        self.assertEqual( self.crawl_queue.dequeue(), 'third' )
        self.assertEqual( self.crawl_queue.dequeue(), 'fourth' )

    def test_crawl_set_length(self):
        length_test_crawl_set = CrawlSet(['one', 'two', 'three'])
        self.assertEqual(len(length_test_crawl_set), 3)
        

    def test_crawl_set___contains__(self):
        """ ensures that the CrawlSet __contains__ function is working correctly """

        c_test_crawl_set = CrawlSet(['one', 'two', 'three'])
        self.assertTrue('one' in c_test_crawl_set)
        self.assertTrue('two' in c_test_crawl_set)
        self.assertTrue('three' in c_test_crawl_set)
        self.assertTrue('not there' not in c_test_crawl_set)
        self.assertFalse('one' not in c_test_crawl_set)
        self.assertFalse('not there' in c_test_crawl_set)

    def test_get_page_str(self):
        """ 
        asserts that the get_page_url function actually retrieves the HTML from a url 
        
        only works when crawling the crawlThis test site
        """
        
        self.assertEqual('pass', get_page_str('test/get_page/', self.test_domain))

    def test_all_links(self):
        """ 
        asserts that all_links is returning all the links in the given HTML 
        by compairing the self reported number of links on a page from crawlThis 
        with the returned number of links

        asserts that all the links returned by all_links are in the page's HTML
        """
        
        page_string = get_page_str('any-page-on-crawlThis', self.test_domain)
        links = all_links(page_string)

        match = re.search('this page has (?P<num>\d+) links', page_string) 
        if match.group():
            num_expected_links = int(match.group('num'))
            self.assertEqual(num_expected_links, len(links))
        else: 
            self.assertEqual("did not figure out how many links we expect to see", False)

        for link in links:
            match = re.search(" href=['\"]%s['\"]" % link, page_string)
            self.assertTrue(match.group())
            
        
if __name__ == '__main__':
    unittest.main()
