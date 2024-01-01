import os
import time
import requests
import json
import logging

from http import HTTPStatus
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib3.exceptions import MaxRetryError, NameResolutionError

from constants import (
    DEFAULT_LOG_LEVEL, ENCODING, MAX_ERROR_MSG, MAX_DEPTH,
    TIMEOUT_SECONDS_PAGE_LOAD, TIMEOUT_SECONDS_REQUEST
)

# define global configuration dictionary
CONFIG = {}

def get_final_url(url, url_original, driver):
    """Retrieve the final URL for a given link.

    Args:
        url (str): The link URL to retrieve.
        url_original (str): The original URL of the page containing the link.
        driver: The Selenium WebDriver instance.

    Returns:
        str: The final URL of the given link or None if an error occurs.
    """
    try:
        driver.get(url)
        return driver.current_url
    except Exception as e:
        logging.error("Page URL: %s", url_original)
        logging.error("Exception retrieving final URL for %s: %s", url, str(e)[:MAX_ERROR_MSG])
        return None


def check_links(base_url, driver, original_url=None, depth=0, max_depth=MAX_DEPTH):
    """Recursively check links on a page and their final URLs.

    Args:
        base_url (str): The base URL of the page to check.
        driver: The Selenium WebDriver instance.
        original_url (str, optional): The original URL of the page (default is None).
        depth (int, optional): The current recursion depth (default is 0).
        max_depth (int, optional): The maximum recursion depth (default is MAX_DEPTH).
    """
    try:
        if original_url is None:
            original_url = base_url

        if depth > max_depth:
            return  # Limit recursion depth

        driver.get(base_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        links = soup.find_all('a', href=True)

        for link in links:
            link_url = link['href']
            link_text = link.text.strip()
            absolute_url = urljoin(base_url, link_url)
            logging.info("Link Text checking: %s", link_text)
            final_url = get_final_url(absolute_url, original_url, driver)
            if final_url is not None:
                final_status_code = requests.head(final_url, allow_redirects=False, timeout=TIMEOUT_SECONDS_REQUEST).status_code
                status_description = HTTPStatus(final_status_code).phrase
                #if final_status_code == HTTPStatus.OK:
                if final_status_code != HTTPStatus.OK or str(HTTPStatus.NOT_FOUND) in final_url:
                    #print(f"Link: {absolute_url} | Text: {link_text} | Final URL: {final_url} | Status Code: {final_status_code} ({status_description})")
                    logging.error("Page URL: %s", original_url)
                    logging.error(
                        "Link: %s | Text: %s | Final URL: %s | Status Code: %s (%s)",
                        absolute_url, link_text, final_url, final_status_code, status_description
                    )
                    if depth + 1 <= max_depth:
                        # Recursively check links on the page that the current link navigates to
                        check_links(final_url, driver, original_url, depth + 1, MAX_DEPTH)
            else:
                pass
                #print(f"Error retrieving final URL for {absolute_url}")
                #print(f"page URL: {original_url}\n")

    except MaxRetryError as mre:
        logging.error("Max retries exceeded for %s: %s", base_url, mre)
    except NameResolutionError as nre:
        logging.error("Name resolution error for %s: %s", base_url, nre)
    except Exception as e:
        logging.error("An unexpected error occurred: %s", str(e)[:MAX_ERROR_MSG])


def set_options():
    """Set Chrome options for running in headless mode.

    Returns:
        ChromeOptions: Configured options for running Chrome in headless mode.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run Chrome in headless mode (no GUI)
    return options


def get_logfile_name():
    """Generate a unique logfile name based on configuration settings.

    Returns:
        str: The complete path of the generated logfile.
    """
    website_url = CONFIG.get('site')
    logging_level = CONFIG.get('logging_level') or DEFAULT_LOG_LEVEL
    dir_logs = CONFIG.get('dir_logs')
    date_format = CONFIG.get('date_format_filename')

    logfile_name = f"{website_url.replace('https://', '').replace('http://', '').replace('/', '_')}_{logging_level.lower()}_{time.strftime(date_format)}.log"

    # Combine DIR_LOGS with the logfile name
    logfile_path = os.path.join(dir_logs, logfile_name)
    # Create the logs directory if it doesn't exist
    logs_dir = os.path.dirname(logfile_path)
    os.makedirs(logs_dir, exist_ok=True)

    return logfile_path


def configure_logging():
    """Configure logging based on the global CONFIG dictionary."""
    logging_level = CONFIG.get('logging_level') or DEFAULT_LOG_LEVEL
    stream = CONFIG.get('log_to_console')

    handlers = [
        logging.StreamHandler() if stream else None,  # Conditionally add StreamHandler
        logging.FileHandler(get_logfile_name())  # Always add FileHandler
    ]

    handlers = [handler for handler in handlers if handler is not None]

    logging.basicConfig(
        level=logging_level,
        format=CONFIG.get("log_format"),
        datefmt=CONFIG.get("date_format_log"),
        handlers=handlers
    )

def load_config():
    """Load configuration settings from the 'config.json' file."""
    try:
        with open('config.json', 'r', encoding=ENCODING) as config_file:
            global CONFIG
            CONFIG = json.load(config_file)
    except FileNotFoundError:
        logging.error("Config file not found. Using default values.")
    except json.JSONDecodeError:
        logging.error("Error decoding JSON in the config file")


def init():
    """Initialize the script by loading configuration and configuring logging."""
    load_config()
    configure_logging()


def main():
    """Main entry point of the script."""
    init()

    website_url =  CONFIG.get('site')
    if website_url:
        logging.info("%s ... checking links ...", website_url)

        options = set_options()

        with webdriver.Chrome(options=options) as driver:
            driver.set_page_load_timeout(TIMEOUT_SECONDS_PAGE_LOAD)
            check_links(website_url, driver)
    else:
        logging.error("Exiting due to missing or invalid config.")

    driver.quit()

if __name__ == "__main__":
    main()