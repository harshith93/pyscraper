import certifi
import urllib3
import time
from bs4 import BeautifulSoup
import re

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
        with open('source.html') as fp:
            soup = BeautifulSoup(fp, 'html.parser')
            return [element.text for element in soup.find_all("script")]

    def find_images(self):
        scripts = self.write()
        images = []
        for script in scripts:
            images_sub = re.findall('([-\w]+\.(?:jpg))', script)
            images += images_sub
        return images

    def find_image_num(self):
        images = self.find_images()
        image_numbers = [image.split('_')[0] for image in images]
        print(image_numbers)


start = time.clock()
scraped = Scraper(url)
scraped.find_image_num()
print(time.clock() - start)

print('Done')
