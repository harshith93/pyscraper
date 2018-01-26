import certifi
import urllib3
import time
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
import time
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

class Scraper(object):
    """docstring for Scraper."""
    def __init__(self):
        super(Scraper, self).__init__()
        # city = city.replace(' ', '%20')
        # self.url = "https://www.flickr.com/search/?text=" + city
        # print(self.url)

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
        print(len(image_numbers))

    def browser_scroll(self, browser):
        SCROLL_PAUSE_TIME = 0.75
        # Get scroll height
        last_height = browser.execute_script("return document.body.scrollHeight")
        print(last_height)
        while True:
            # Scroll down to bottom
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)
            # Calculate new scroll height and compare with last scroll height
            new_height = browser.execute_script("return document.body.scrollHeight")
            print(new_height)
            if new_height == last_height:
                try:
                    browser.find_element_by_css_selector('.infinite-scroll-load-more .alt').send_keys(Keys.SPACE)
                    time.sleep(SCROLL_PAUSE_TIME)
                    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    return self.browser_scroll(browser)
                finally:
                    break
            last_height = new_height


    def sel_scrape(self, city):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        browser = webdriver.Chrome()
        browser.get("https://www.flickr.com/search/?text=" + city)
        self.browser_scroll(browser)
        elements = browser.find_elements_by_css_selector('.photo-list-photo-interaction .overlay')
        for element in elements:
            print(element.get_attribute("href"))


def get_link(element):
    return element.get_attribute("href")


class ImageInfo(object):
    """docstring for ImageInfo."""
    def __init__(self):
        super(ImageInfo, self).__init__()

    def grab_info(self, element):
        url = element.get_attribute("href")
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        browser = webdriver.Chrome(chrome_options=chrome_options)
        browser.get(url)
        image = browser.find_element_by_class_name('main-photo')
        print(image.get_attribute('src'))


cities = input("Please enter the names of the cities separated by comma: ")
#cities = [city for city in cities.split(',')]
#cities = [Scraper("%s" %(city)) for city in cities]
print("Processing...")

NUM_WORKERS = 4
start_time = time.time()
futures = None
with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
    futures = {executor.submit(Scraper().sel_scrape, city.replace(' ', '%20')) for city in cities.split(',')}
    concurrent.futures.wait(futures)

end_time = time.time()


# NUM_WORKERS = 10
# with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
#     futures = {executor.submit(Scraper().sel_scrape, city.replace(' ', '%20')) for city in cities.split(',')}
#     concurrent.futures.wait(futures)

print("Time for Concurrent: %s secs" % (end_time - start_time))
print('Done')
