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
from multiprocessing import Pool
import multiprocessing
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
import pickle


class Scraper(object):
    """docstring for Scraper."""
    def __init__(self):
        super(Scraper, self).__init__()


    def crawl(self, url):
        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',
                                    ca_certs=certifi.where())
        response = http.request('GET', url)
        try:
            result = response.data.decode()
        except Exception as e:
            print("Results no")
            print(e)
        return result

    def get_info_page(self, url):
        with self.crawl(url) as source:
            # soup = BeautifulSoup(fp, 'html.parser')
            print(url)

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
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)
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
        browser = webdriver.Chrome(chrome_options=chrome_options)
        print("https://www.flickr.com/search/?text=" + city)
        browser.get("https://www.flickr.com/search/?text=" + city)
        self.browser_scroll(browser)
        elements = browser.find_elements_by_css_selector('.photo-list-photo-interaction .overlay')
        return [element.get_attribute("href") for element in elements]


    def get_info_city(self, city):
        links_list = self.sel_scrape(city)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            try:
                futures = [executor.submit(self.image_info, link) for link in links_list]
                for future in as_completed(futures):
                    print(future.result())
            except Exception as e:
                print(e)

    def image_info(self, link):
        self.get_info_page(link)
        return 1

    def get_link(self, element):
        return element.get_attribute('href')

cities = input("Please enter the names of the cities separated by comma: ")
cities = [city for city in cities.split(',')]
cities = [city.replace(' ', '%20') for city in cities]
print("Processing...")

NUM_WORKERS = 4
start_time = time.time()
# scraped = Scraper()
# print(scraped.scrape_cities(cities))
with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
    futures = [executor.submit(Scraper().get_info_city, city) for city in cities]
    concurrent.futures.wait(futures)

end_time = time.time()

print("Time for Concurrent: %s secs" % (end_time - start_time))
print('Done')
