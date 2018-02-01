import certifi
import urllib3
import time
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from multiprocessing import Pool
import multiprocessing
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
import sqlite3


class Scraper(object):
    """docstring for Scraper."""
    def __init__(self):
        super(Scraper, self).__init__()

    def browser_scroll(self, browser):
        SCROLL_PAUSE_TIME = 0.75
        last_height = browser.execute_script("return document.body.scrollHeight")
        while True:
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)
            new_height = browser.execute_script("return document.body.scrollHeight")
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
        browser.get("https://www.flickr.com/search/?text=" + city)
        self.browser_scroll(browser)
        elements = browser.find_elements_by_css_selector('.photo-list-photo-interaction .overlay')
        if len(elements) == 0:
            return None
        else:
            return [element.get_attribute("href") for element in elements]

    def get_info_city(self, city):
        links_list = self.sel_scrape(city)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            try:
                futures = [executor.submit(self.crawl, link) for link in links_list]
                concurrent.futures.wait(futures)
                return True
            except Exception as e:
                print(e)
        return False

    def crawl(self, url):
        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',
                                    ca_certs=certifi.where())
        response = http.request('GET', url)
        try:
            result = response.data.decode()
            soup = BeautifulSoup(result, "html.parser")
            image = soup.find("img", class_= "main-photo is-hidden").get("src")
            script = soup.find("script", class_="modelExport")
            geo = re.compile('(?<=\_flickrModelRegistry":"photo-geo-models",)(.*?)(?=\,"accuracy")')
            geo = [geo.split(':') for geo in geo.findall(str(script))[0].split(',')]
            conn = sqlite3.connect('scraper')
            c = conn.cursor()
            if geo[0][1] == 'true':
                query = "INSERT INTO images VALUES(\"%s\", %f, %f)" %(image, float(geo[1][1]), float(geo[2][1]))
                c.execute(query)
            else:
                query = "INSERT INTO images VALUES(\"%s\", null, null)" %(image)
                c.execute(query)
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(e)
        return False


    def start_scraping(self, cities):

        cities = [city.replace(' ', '%20') for city in cities]
        NUM_WORKERS = 4
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
                futures = [executor.submit(self.get_info_city, city) for city in cities]
                concurrent.futures.wait(futures)
                return True
        except Exception as e:
            print(e)
            return False
