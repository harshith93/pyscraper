import certifi
import urllib3
import time

url = "https://www.flickr.com/search/?text=paris"


class Scraper(object):
    """docstring for Scraper."""
    def __init__(self, url):
        super(Scraper, self).__init__()
        self.url = url

    def crawl(self):
        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',
                                    ca_certs=certifi.where())
        response = http.request('GET', self.url)
        result = response.data
        return result

    def write(self):
        f = open('source.html', 'w')
        f.write(self.crawl().decode())
        f.close()
        return

scraped = Scraper(url)
scraped.write()


start = time.clock()
if "2163641698" in open('source.html').read():
    print(True)
else:
    print(False)
print(time.clock() - start)

print('Done')
