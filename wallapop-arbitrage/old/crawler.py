from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotInteractableException, ElementClickInterceptedException   
from datetime import datetime
import pandas as pd
import re
import numpy as np
from time import sleep
import urllib.parse
import sys



# Decorators
def time_it(func):
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        print(f'{func.__name__} == {start_time}')
        result = func(*args, **kwargs)
        elapsed_time = datetime.now() - start_time
        print(f"    {func.__name__} == took: {elapsed_time}")
        return result
    return wrapper


def print_update(func):
    def wrapper(*args, **kwargs):
        print(f'{func.__name__}')
        return func(*args, **kwargs)
    return wrapper


def reject_cookies(driver, retries=3):
    try:
        WebDriverWait(driver, retries).until(EC.element_to_be_clickable((By.ID, 'onetrust-reject-all-handler')))
        driver.find_element(By.ID, 'onetrust-reject-all-handler').click()
    except (NoSuchElementException, TimeoutException, ElementNotInteractableException, ElementClickInterceptedException):
        print(f'    Rejecting cookies failed. Attempt:{-retries + 4}')
        retries -= 1
        if retries > 0:
            reject_cookies(driver, retries=retries)


def skip_tutorial(driver, retries=3):
    try:
        WebDriverWait(driver, retries).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'walla-button.TooltipWrapper__skip')))
        driver.find_element(By.CSS_SELECTOR, 'walla-button.TooltipWrapper__skip').click()
        driver.find_element(By.CSS_SELECTOR, 'walla-button.TooltipWrapper__skip').click()
        driver.find_element(By.CSS_SELECTOR, 'walla-button.TooltipWrapper__skip').click()
    except (NoSuchElementException, TimeoutException, ElementNotInteractableException, ElementClickInterceptedException):
        print(f'    Skiping tutorial failed. Attempt {-retries + 4}')
        retries -= 1
        if retries > 0:
            skip_tutorial(driver, retries=retries)


# @print_update
def setup_driver():
    options = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--log-level=4")
    options.add_argument("--disable-extensions")
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    driver.get('https://es.wallapop.com/app/search?filters_source=category_navigation&latitude=40.41956&longitude=-3.69196')

    reject_cookies(driver)
    skip_tutorial(driver)

    return driver


def load_more(driver, retries=3):
    # Clicks button that initiates infinite scroll dynamic listings
    try:
        WebDriverWait(driver, retries).until(EC.element_to_be_clickable((By.ID, 'btn-load-more')))
        driver.find_element(By.ID, 'btn-load-more').click()
    except (NoSuchElementException, TimeoutException, ElementNotInteractableException, ElementClickInterceptedException):
        print(f'    Load_more not clicked. Attempt: {-retries + 4}')
        retries -= 1
        if retries > 0:
            load_more(driver, retries=retries)


def wait_listings(driver, retries=3): # Implement a way to detect 'no listings found' and quick when that is found
    try:
        WebDriverWait(driver, retries).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.ItemCardList__item')))
        return True
    except (NoSuchElementException, TimeoutException, ElementNotInteractableException, ElementClickInterceptedException):
        print(f'    Listings not present. Attempt:{-retries + 4}')
        retries -= 1

    try:
        WebDriverWait(driver, retries).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'p.ErrorBox__title')))
        return False
    except (NoSuchElementException, TimeoutException, ElementNotInteractableException, ElementClickInterceptedException):
        if retries > 0:
            wait_listings(driver, retries=retries)


# Explorer scraping functions
# @print_update
def scrape_explorer(driver, object_id=None):
    # Scrapes listings displayed in explorer
    scrapings = []
    cards = driver.find_elements(By.CSS_SELECTOR, 'a.ItemCardList__item')
    for card in cards:
        title = card.get_attribute('title')
        href = card.get_attribute('href')
        listing_id = href.split('-')[-1]
        num_images = len(card.find_elements(By.TAG_NAME, 'li'))
        img_scr = card.find_element(By.TAG_NAME, 'img').get_attribute('src')
        date_scraped = datetime.now().strftime('%d-%m-%y')

        price = card.find_element(By.CSS_SELECTOR, 'span.ItemCard__price').text.strip()
        price = float(re.sub(r'[^\d,]', '', price).replace(',', '.'))
        
        try:
            if card.find_element(By.CSS_SELECTOR, 'p.ItemCard__highlight-text.pb-2'):
                featured = True
            else:
                featured = False
        except NoSuchElementException:
            featured = False

        shadow_hosts = card.find_elements(By.CSS_SELECTOR, 'wallapop-badge')
        shipping, reserved, walla_pro = 0, False, False
        for shadow_host in shadow_hosts:
            shadow_root = driver.execute_script('return arguments[0].shadowRoot', shadow_host)
            span = shadow_root.find_element(By.CSS_SELECTOR, 'span').text.strip() 
            if span == 'Sólo venta en persona':
                shipping = 0
            elif span == 'Envío disponible':
                shipping = 1
            elif span == 'Envío gratis':
                shipping = 2
            elif span == 'Reservado':
                reserved = True
            elif span == 'Reacondicionado':
                walla_pro = True

        scrapings.append({
            'title': title,
            'href': href,
            'product_id': np.nan,
            'object_id': object_id,
            'listing_id': listing_id,
            'num_images': num_images,
            'img_scr': img_scr,
            'date_last_scraped': date_scraped,
            'date_first_scraped': np.nan,
            'price': price,
            'featured': featured,
            'shipping' : shipping,
            'reserved' : reserved,
            'walla_pro' : walla_pro,
        })
        
    return scrapings


# @print_update
def scroll_explorer(driver, object_id=None, max_scrolls=50):
    previous_height = driver.execute_script("return document.body.scrollHeight")
    sleep_time = 0.1
    count = 0
    timer = datetime.now()

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        count += 1
        if count == max_scrolls:
            if check_scraping(driver, timer, False, object_id=object_id):
                return True
            else:
                return False

        try:
            WebDriverWait(driver, sleep_time).until(lambda driver: driver.execute_script("return document.body.scrollHeight") != previous_height)
            sleep_time /= 2
            previous_height = driver.execute_script("return document.body.scrollHeight")
        except TimeoutException:
            sleep_time += sleep_time
            if sleep_time > 12:
                if check_scraping(driver, timer, True, object_id=object_id):
                    return True
                else:
                    return False


# @print_update
def check_scraping(driver, timer, bool, object_id=None):
    global scraped

    if bool:
        pass
    else:
        sleep(1)
        
    # Get scrapings and check if they already exist in global
    scrapings = scrape_explorer(driver, object_id=object_id)
    temp = pd.DataFrame(scrapings)
    if temp['listing_id'].isin(scraped['listing_id']).any():
        print('    server is repeating listings')
        if temp['listing_id'].isin(scraped['listing_id']).all():
            print('    scroll completely redundant')
            return True
        else:
            scraped = pd.concat([scraped, temp]).drop_duplicates()
    else:
        scraped = pd.concat([scraped, temp]).drop_duplicates()
    
    # Print stats
    elem_count = len(scrapings)
    clear_explorer(driver)
    timespent = datetime.now() - timer
    print(f'    current scrape = {elem_count}')
    print(f'    scrape time = {timespent}')
    print(f'    efficiency = {timespent/elem_count}')
    print(f'    total scraped = {len(scraped)}')

    if bool:
        return True
    else:
        return scroll_explorer(driver, object_id=object_id)


# @print_update
def clear_explorer(driver):
    driver.execute_script("window.scrollTo(0, 0);")

    # Find elements and delete all siblings
    element = driver.find_element(By.CSS_SELECTOR, 'a.ItemCardList__item')
    parent = element.find_element(By.XPATH, '..')
    siblings = parent.find_elements(By.XPATH, '*')
    for sibling in siblings:
        driver.execute_script("arguments[0].remove();", sibling)


@time_it
def crawl_explorer(instance):
    global scraped

    pending_urls = pd.read_csv(f'wallapop-arbitrage/data/urls/urls_{instance}.csv')
    for i, url in pending_urls['explorer_url'].items():
        scraped = pd.DataFrame(columns=['title','href','product_id','object_id','listing_id','num_images','img_scr','date_last_scraped','date_first_scraped','price','featured','shipping','reserved','walla_pro'])
        complete = False
        time = datetime.now()

        driver = setup_driver()
        driver.get(url + '&order_by=price_low_to_high')
        if wait_listings(driver):
            try:
                load_more(driver)
                complete = scroll_explorer(driver, pending_urls.iloc[i]['object_id'])
                driver.quit()
            except Exception as e:
                print(f'\nLow-to-high error: {e}')
                driver.quit()
            print(f'\n{len(scraped)} low-to-high scraped')

            if not complete:
                driver = setup_driver()
                driver.get(url + '&order_by=price_high_to_low')
                if wait_listings(driver):
                    try:
                        load_more(driver)
                        scroll_explorer(driver, pending_urls.iloc[i]['object_id'])
                        driver.quit()
                    except Exception as e:
                        print(f'\nHigh-to-low error: {e}')
                        driver.quit()
                    print(f'\n{len(scraped)} high-to-low scraped')
                else:
                    driver.quit()
            else:
                print('complete')
        else:
            driver.quit()

        # Update files
        pending_urls.at[i, 'date_scraped'] = datetime.now()
        if scraped.empty:
            pending_urls.at[i, 'scrape_empty'] = True
            pending_urls.to_csv(f'wallapop-arbitrage/data/urls/urls_{instance}.csv', index=False)
        else: 
            pending_urls.at[i, 'scrape_empty'] = False
            try:
                listings = pd.read_csv(f'wallapop-arbitrage/data/listings/{pending_urls.iloc[i]['object_id']}_{i}_listings.csv')
            except FileNotFoundError:
                listings = pd.DataFrame(columns=['title','href','product_id','object_id','listing_id','num_images','img_scr','date_last_scraped','date_first_scraped','price','featured','shipping','reserved','walla_pro'])

            if scraped.isin(listings.to_dict(orient='list')).all().all():
                pending_urls.at[i, 'redundant_url'] = True
            else:
                pending_urls.at[i, 'redundant_url'] = False
                listings = pd.concat([listings, scraped]).drop_duplicates()
                listings.to_csv(f'wallapop-arbitrage/data/listings/{pending_urls.iloc[i]['object_id']}_{i}_listings.csv', index=False)
            
            pending_urls.to_csv(f'wallapop-arbitrage/data/urls/urls_{instance}.csv', index=False)

        print(f'\n#### {instance}scraper = URL {i} took: {datetime.now() - time} #######################################\n')

    print('All urls scraped')


if __name__ == "__main__":
    instance = sys.argv[1]
    scraped = []
    crawl_explorer(instance)