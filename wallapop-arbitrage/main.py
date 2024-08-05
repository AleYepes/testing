import multiprocessing
import subprocess
import pandas as pd
import numpy as np
from datetime import datetime
import math
import os


def generate_explorer_urls(product_id=None, category_id=24200):
    # gets the corresponding urls to wallapop listing explorer
    base = 'https://es.wallapop.com/app/search?'
    urls = []

    if product_id:
        pass ## Do later
        # url = url if (product_id == None) else url + f'keywords={urllib.parse.quote(product_id)}&'
    else:
        if category_id == 24200:
            object_type_ids = [9447, 9487, 10175, 24102]
            for object_id in object_type_ids:
                url = base + f'category_ids={category_id}&filters_source=quick_filters&latitude=40.41956&longitude=-3.69196&object_type_ids={object_id}&'
                urls += split_explorer_url(url, product_id=product_id, category_id=category_id, object_id=object_id)
        else:
            print('category not supported')

    return urls


def split_explorer_url(url, product_id=None, category_id=None, object_id=None):
    # breaks up url into smaller subsets to divide up scrape load
    urls = []

    if product_id:
        # IGNORE write later after figuring out product_id classification module
        pass
    else:
        price_range, step_size = 1000, 1
        loops = round(price_range/step_size)

        for i in range(loops):
            min = (step_size * i)
            max = (step_size * (i+1))
            if i == 0:
                pricequery = f'max_sale_price={max}'
            elif i + 1 == len(range(loops)):
                pricequery = f'min_sale_price={min+.01}'
            else:
                pricequery = f'min_sale_price={min+.01}&max_sale_price={max}'

            urls.append({
                'explorer_url': url + pricequery,
                'product_id': product_id,
                'category_id': category_id,
                'object_id': object_id,
                'date_scraped': np.nan,
                'scrape_empty': np.nan,
                'redundant_url': np.nan,
            })
    return urls


def join_urls():
    directory = 'wallapop-arbitrage/data/urls/'
    urls = []
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            filepath = os.path.join(directory, filename)
            url = pd.read_csv(filepath)
            urls.append(url)
    try:    
        return pd.concat(urls)
    except ValueError:
        return pd.DataFrame()
    

def run_crawler(instance):
    print(f"Starting worker instance {instance}")
    subprocess.run(['python', 'wallapop-arbitrage/crawler.py', str(instance)])
    print(f"Worker instance {instance} has finished")



def main(custom_url=False, category_id = 24200, crawler_count=2):
    if custom_url:
        urls = pd.DataFrame([{'explorer_url':custom_url, 'product_id':np.nan}])
        pending_urls = urls
    else:
        if join_urls().empty:
            try:
                urls = pd.read_csv('data/urls.csv')
            except FileNotFoundError:
                urls = pd.DataFrame(generate_explorer_urls(category_id=category_id))
        else:
            urls = join_urls()
        urls['date_scraped'] = pd.to_datetime(urls['date_scraped'], errors='coerce')
        current_week = datetime.now().isocalendar()[:2] # isocalendar() returns -> year, week, weekday
        pending_urls = urls[urls['date_scraped'].apply(lambda x: x.isocalendar()[:2] if pd.notnull(x) else None) != current_week]

        total_listings = len(pending_urls)
        if crawler_count >= total_listings:
            crawler_count = total_listings
        else:
            listings_per_crawler = math.floor(total_listings / crawler_count)

        processes = []
        for i in range(crawler_count):
            if i == (crawler_count - 1):
                pending_urls.iloc[listings_per_crawler * i:].to_csv(f'wallapop-arbitrage/data/urls/urls_{i}.csv', index=False)
            else:
                pending_urls.iloc[listings_per_crawler * i:listings_per_crawler * (i+1)].to_csv(f'wallapop-arbitrage/data/urls/urls_{i}.csv', index=False)

            p = multiprocessing.Process(target=run_crawler, args=(i,))
            processes.append(p)
            p.start()
        for p in processes:
            p.join()

    print("All worker instances have finished")

if __name__ == "__main__":
    main()
