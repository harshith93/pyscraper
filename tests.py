import scraper
import time
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
import unittest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class ScraperTest(unittest.TestCase):

    def setUp(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)

    def test_start_scraping(self):
        cities = ['paris']
        urls = scraper.Scraper()
        value = urls.start_scraping(cities)
        self.assertEqual(True, value)

    def tearDown(self):
        self.driver.close()


if __name__ == "__main__":
    unittest.main()
