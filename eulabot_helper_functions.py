import urllib
import re

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
        print 'error in all_links helper function'
        return None

