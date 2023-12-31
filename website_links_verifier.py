import json
from http import HTTPStatus
from urllib.parse import urljoin
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib3.exceptions import MaxRetryError, NameResolutionError

from constants import ENCODING, MAX_ERROR_MSG

def get_final_url(url, driver):
    try:
        driver.get(url)
        return driver.current_url
    except Exception as e:
        print(f"Error retrieving final URL for {url}: {str(e)[0:MAX_ERROR_MSG]}")
        return None

def check_links(base_url):
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Run Chrome in headless mode (no GUI)

        with webdriver.Chrome(options=options) as driver:
            driver.set_page_load_timeout(10)

            driver.get(base_url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            links = soup.find_all('a', href=True)

            for link in links:
                link_url = link['href']
                link_text = link.text.strip()
                absolute_url = urljoin(base_url, link_url)

                final_url = get_final_url(absolute_url, driver)
                if final_url is not None:
                    final_status_code = requests.head(final_url, allow_redirects=False).status_code
                    status_description = HTTPStatus(final_status_code).phrase
                    if final_status_code != HTTPStatus.OK or str(HTTPStatus.NOT_FOUND) in final_url:
                        print(f"Link: {absolute_url} | Text: {link_text} | Final URL: {final_url} | Status Code: {final_status_code} ({status_description})")
                else:
                    print(f"Error retrieving final URL for {absolute_url}")

    except MaxRetryError as mre:
        print(f"Max retries exceeded for {base_url}: {mre}")
    except NameResolutionError as nre:
        print(f"Name resolution error for {base_url}: {nre}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)[0:MAX_ERROR_MSG]}")

def read_config(key):
    try:
        with open('config.json', 'r', encoding=ENCODING) as config_file:
            config_data = json.load(config_file)
            return config_data.get(key)
    except FileNotFoundError:
        print("Config file not found.")
        return None
    except json.JSONDecodeError:
        print("Error decoding JSON in the config file.")
        return None

def main():
    website_url = read_config('site')

    if website_url:
        print(f"{website_url} ... checking links ...")
        check_links(website_url)
    else:
        print("Exiting due to missing or invalid config.")

if __name__ == "__main__":
    main()
