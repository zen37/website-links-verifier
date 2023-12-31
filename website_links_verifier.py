import requests
import json

from http import HTTPStatus
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib3.exceptions import MaxRetryError, NameResolutionError

from constants import ENCODING, MAX_ERROR_MSG, TIMEOUT_SECONDS_PAGE_LOAD, TIMEOUT_SECONDS_REQUEST

def get_final_url(url, url_original, driver):
    try:
        driver.get(url)
        return driver.current_url
    except Exception as e:
        print(f"Exception retrieving final URL for {url}: {str(e)[0:MAX_ERROR_MSG]}")
        print(f"page URL: {url_original}\n")
        return None

def check_links(base_url, driver, original_url=None):
    try:
        if original_url is None:
            original_url = base_url

        driver.get(base_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        links = soup.find_all('a', href=True)

        for link in links:
            link_url = link['href']
            link_text = link.text.strip()
            absolute_url = urljoin(base_url, link_url)
            print("Link Text checking:", link_text)
            final_url = get_final_url(absolute_url, original_url, driver)
            if final_url is not None:
                final_status_code = requests.head(final_url, allow_redirects=False, timeout=TIMEOUT_SECONDS_REQUEST).status_code
                status_description = HTTPStatus(final_status_code).phrase
                #if final_status_code == HTTPStatus.OK:
                if final_status_code != HTTPStatus.OK or str(HTTPStatus.NOT_FOUND) in final_url:
                    print(f"Link: {absolute_url} | Text: {link_text} | Final URL: {final_url} | Status Code: {final_status_code} ({status_description})")
                    print(f"Page URL: {original_url}\n")
                    # Recursively check links on the page that the current link navigates to
                    check_links(final_url, driver, original_url)
            else:
                pass
                #print(f"Error retrieving final URL for {absolute_url}")
                #print(f"page URL: {original_url}\n")

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

        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Run Chrome in headless mode (no GUI)

        with webdriver.Chrome(options=options) as driver:
            driver.set_page_load_timeout(TIMEOUT_SECONDS_PAGE_LOAD)
            check_links(website_url, driver)
    else:
        print("Exiting due to missing or invalid config.")

    driver.quit()

if __name__ == "__main__":
    main()