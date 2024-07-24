import logging
import random
import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from pyvirtualdisplay import Display
from prettytable import PrettyTable
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import os
import sys

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

base_url = 'https://icargo.schedules.qwyk.io/'
proxies = ''
if os.getenv('PROXIES'):
    proxies = os.getenv('PROXIES').split(',')

def get_random_proxy():
    """Return a random proxy from list."""
    return random.choice(proxies)

def initialize_selenium_driver(use_webdriver_manager=False, proxy=None):
    """Initialize the Selenium WebDriver."""
    logging.info("Initializing Selenium WebDriver.")
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    if proxy:
        options.add_argument(f'--proxy-server={proxy}')
    
    try:
        if use_webdriver_manager:
            driver = webdriver.Chrome(service=ChromeService(executable_path=ChromeDriverManager().install()), options=options)
        else:
            driver = webdriver.Chrome(service=ChromeService(executable_path='/usr/local/bin/chromedriver-linux64/chromedriver'), options=options)

    except WebDriverException as e:
        raise Exception(f"Error initializing Selenium WebDriver: {e}")
    
    return driver

def get_bearer_token(driver):
    """Retrieve bearer token using Selenium WebDriver."""
    driver.get(base_url)
    try:
        logging.info("Waiting for window.PAT to be defined.")
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return typeof window.PAT !== 'undefined';")
        )
        token = driver.execute_script("return window.PAT;")
        logging.info("Bearer token retrieved successfully.")
    except TimeoutException:
        raise Exception("Timeout while waiting for window.PAT to be defined.")
    except WebDriverException as e:
        raise Exception(f"Error while loading the page or retrieving the token: {e}")
    except Exception as e:
        raise Exception((f"Error General: {e}"))

    if token is None:
        raise Exception("Token not found in window.PAT")
    return f"Bearer {token}"

def check_locode_exist(token, locode, way, proxy=None):
    """Check if a locode exists."""
    url = f"{base_url}api/schedules/c/2/csl/locations/{way}/{locode}"
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, proxies={"http": proxy, "https": proxy} if proxy else None)
        response.raise_for_status()
        
        if not response.json():
            raise Exception(f"Locode {locode} does not exist")
        
        if len(response.json()) > 1:
            raise Exception(f"Multiple locodes found for {locode}")
        
        return True
    except requests.RequestException as e:
        logging.error(f"An error occurred while checking locode: {e}")
        return False

def fetch_schedules(token, origin_locode, destination_locode, proxy=None):
    """Fetch schedules from the API."""
    url = f"{base_url}api/schedules/c/2/csl/{origin_locode}/{destination_locode}"
    logging.info(f"Fetching schedules from URL: {url}")
    headers = {
        "Authorization": token,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers,  proxies={"http": proxy, "https": proxy} if proxy else None)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        raise(f"An error occurred while fetching schedules: {e}")

    schedules = []
    for schedule in data:
        carrier = schedule['carrier']['display_name']
        voyage = schedule['voyage']
        etd = schedule['etd']
        eta = schedule['eta']
        service = schedule['service']
        schedules.append((carrier, voyage, etd, eta, service))

    return schedules

def display_schedules(schedules):
    """Display schedules in a table format."""
    table = PrettyTable()
    table.field_names = ["Carrier", "Voyage", "ETD", "ETA", "Service"]
    for schedule in schedules:
        table.add_row(schedule)
    print(table)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        logging.error("Usage: python fetch_schedules.py <origin_locode> <destination_locode> [--use-webdriver-manager]")
        sys.exit(1)

    origin_locode = sys.argv[1]
    destination_locode = sys.argv[2]

    #web driver manager as option
    use_webdriver_manager = "--use-webdriver-manager" in sys.argv
    
    use_proxy = "--use-proxy" in sys.argv

    try:
        display = Display(visible=0, size=(1920, 1080))
        display.start()

        proxy = get_random_proxy() if use_proxy else None
        logging.info(f"Using Proxy {proxy}")

        driver = initialize_selenium_driver(use_webdriver_manager=use_webdriver_manager, proxy=proxy)
        token = get_bearer_token(driver)

        if not check_locode_exist(token, origin_locode, "origin", proxy=proxy):
            logging.error("Invalid origin_locode")
            sys.exit(1)

        if not check_locode_exist(token, destination_locode, "destination", proxy=proxy):
            logging.error("Invalid origin_locode")
            sys.exit(1)

        schedules = fetch_schedules(token, origin_locode, destination_locode, proxy=proxy)
        if schedules:
            display_schedules(schedules)
        else:
            logging.info("No schedules found.")
    except Exception as e:
        logging.error(f"{e}")
    finally:
        driver.quit()
        display.stop()
