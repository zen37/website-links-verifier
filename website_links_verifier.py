import json
from http import HTTPStatus
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from urllib3.exceptions import MaxRetryError, NameResolutionError

from constants import ENCODING

def get_final_url(url):
    try:
        response = requests.head(url, allow_redirects=True)
        return response.url
    except Exception as e:
        print(f"Error retrieving final URL for {url}: {e}")
        return None

def check_links(base_url):
    try:
        with requests.Session() as session:
            response = session.get(base_url)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                links = soup.find_all('a', href=True)

                for link in links:
                    link_url = link['href']
                    link_text = link.text.strip()  # Extract text associated with the link
                    absolute_url = urljoin(base_url, link_url)

                    final_url = get_final_url(absolute_url)
                    if final_url is not None:
                        final_status_code = session.head(final_url).status_code
                        status_description = HTTPStatus(final_status_code).phrase
                        print(f"Link: {absolute_url} | Text: {link_text} | Final URL: {final_url} | Status Code: {final_status_code} ({status_description})")
                    else:
                        print(f"Error retrieving final URL for {absolute_url}")

            else:
                print(f"Failed to retrieve the page. Status Code: {response.status_code}")

    except MaxRetryError as mre:
        print(f"Max retries exceeded for {base_url}: {mre}")
    except NameResolutionError as nre:
        print(f"Name resolution error for {base_url}: {nre}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

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
