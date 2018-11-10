from selenium import webdriver
from selenium.common.exceptions import *

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from selenium.webdriver.chrome.options import Options  

from urllib import parse


BASE_URL = 'https://translate.google.cz/'
DATA_DIR = 'data/'

CHARACTER_LIMIT = 4500


def iter_chunks(data: list):
    remaining_limit = CHARACTER_LIMIT
    chunk = []

    for line in data:
        chunk.append(line)
        remaining_limit -= len(line)

        if remaining_limit <= 0:
            yield "\n".join(chunk)

            chunk = []
            remaining_limit = CHARACTER_LIMIT

    yield "\n".join(chunk)


def translate(query: str, from_lang='cs', to_lang='en') -> list:
    lang_mod = f"#{from_lang}/{to_lang}/"
    quoted_query = lang_mod + parse.quote(query)
    
    url = parse.urljoin(BASE_URL, quoted_query)
    driver.get(url)
    
    translation = driver.find_element_by_id('result_box')
    
    return translation.text.split(sep='\n')


def swap_languages():
    WebDriverWait(driver, timeout=3).until(
        EC.element_to_be_clickable((By.ID, 'gt-swap'))
    )

    swap_button = driver.find_element_by_id('gt-swap')
    swap_button.click()


chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=chrome_options)
driver.get(BASE_URL)

driver.implicitly_wait(0.25)
