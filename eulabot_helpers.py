import urllib
import re
import os

def default_payload(page_str):
    if page_str:
        print "default payload ran for:", page_str[:50], '...'
    else:
        print "there was no page string"

def default_url_handler(urls, do_not_crawl_list, crawl_queue):
    for url in urls:
        if url not in do_not_crawl_list:
            crawl_queue.enqueue(url)
            

def read_page_str(url, domain):
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

def log(log_string, log_file_name):
    """
    adds log string to the end of log file
    """

    log_file = open(log_file_name, 'a')
    log_file.write('%s\n' % log_string)
    log_file.close()
