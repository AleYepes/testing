from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd
import re
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import requests
import time


# def scrape_ocasion(url):
#     # Set no image load
#     options = webdriver.ChromeOptions()
#     prefs = {"profile.managed_default_content_settings.images": 2}
#     options.add_experimental_option("prefs", prefs)

#     # Load driver
#     driver = webdriver.Chrome(options=options)
#     driver.get(url)

#     # Scroll until seeMoreCars_button disappears
#     WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "seeMoreCars_button__WXdaL")))
#     while True:
#         try:
#             driver.execute_script("arguments[0].scrollIntoView();", driver.find_elements(By.CLASS_NAME, "cardVehicle_card__LwFCi")[-2])
#             WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".seeMoreCars_button__WXdaL")))
#         except NoSuchElementException:
#             print('no such element')
#             break
#         except TimeoutException:
#             break

#     html = driver.page_source
#     driver.quit()

#     soup = BeautifulSoup(html, 'html.parser')
#     html = soup.find_all('div', class_='cardVehicle_card__LwFCi')

#     return html


# def parse_ocasion(html):
#     cars_data = []
#     lens = []
#     for car in html:
#         discount = car.find('p', class_='topLayer_discount__8zFJc')
#         if discount is None:
#             status = 'Available'
#         else:
#             discount = car.find('p', class_='topLayer_discount__8zFJc').text.capitalize()
#             if discount == 'Reservado':
#                 status = 'Reservado'
#                 discount = None
#             elif discount == 'Vendido':
#                 status = 'Vendido'
#                 discount = None
#             else:
#                 status = 'Available'
#                 discount = int(re.sub(r'\D', '', discount))
        
#         title = car.find_all('span', class_='cardVehicle_spot__e6YZx')
#         if len(title) == 2:
#             full_price = title[1].text
#             full_price = int(re.sub(r'\D', '', full_price))
#         else:
#             full_price = None
#         title = title[0].text

#         description = car.find_all('span', class_='cardVehicle_finance__SG6JV')
#         discounted_price = description[1].text
#         discounted_price = int(re.sub(r'\D', '', discounted_price))
#         description = description[0].text

#         details = car.find_all('span', class_='characteristics_elements__Mb1S_')
#         details = [detail.text for detail in details]
#         year = int(details[0])
#         mileage = details[1]
#         mileage = int(re.sub(r'\D', '', mileage))
#         fuel = details[2]
#         cv = details[3]
#         cv = int(re.sub(r'\D', '', cv))
#         transmission = details[4].capitalize()
#         owner = None
#         warranty = None
#         libro = None
#         vista = None
#         try:
#             if details[5] == 'Vista 360º':
#                 vista = details[5]
#             elif details[5] == 'Único propietario':
#                 owner = details[5]
#             elif details[5] == 'Garantía del fabricante':
#                 warranty = details[5]
#             elif details[5] == 'Libro de revisiones':
#                 libro = details[5]
#             else:
#                 vista = None
#         except IndexError:
#             vista = None
#         try:
#             if details[6] == 'Único propietario':
#                 owner = details[6]
#             elif details[6] == 'Garantía del fabricante':
#                 warranty = details[6]
#             elif details[6] == 'Libro de revisiones':
#                 libro = details[6]
#             else:
#                 owner = None
#         except IndexError:
#             owner = None
#         try:
#             if details[7] == 'Garantía del fabricante':
#                 warranty = details[7]
#             elif details[7] == 'Libro de revisiones':
#                 libro = details[7]
#             else:
#                 warranty = None
#         except IndexError:
#             warranty = None
#         try:
#             libro = details[8]
#         except IndexError:
#             libro = None

#         city = car.find('div', class_='cardVehicle_dealer__41Xs5').text.split('-')
#         if len(city) == 2:
#             district = city[1]
#             city = city[0]
#         else:
#             district = None
#             city = city[0]
#         url = car.find('a', class_="cardVehicle_link__l8xYT")['href']
#         url = 'https://www.ocasionplus.com' + url

#         cars_data.append([discount, status, title, full_price, description, discounted_price, year, mileage, fuel, cv, transmission, vista, owner, warranty, libro, city, district, url])
        
#     df = pd.DataFrame(cars_data, columns=["discount", "status", "title", "full_price", "description", "discounted_price", "year", "mileage", "fuel", "cv", "transmission", "vista", "owner", "warranty", "libro", 'city', 'district', 'url'])

#     return df


# def impute_missing(row):
#     if pd.isna(row['discount']):
#         imputed_value = row['full_price'] - row['discounted_price']
#         return imputed_value
#     else:
#         return row['discount']
    

# def scrape_autoscout(url):
#     response = requests.get(url)
#     soup = BeautifulSoup(response.text, 'html.parser')

#     # Find all car listings on the page
#     cars = soup.find_all('article', class_='cldt-summary-full-item')

#     # Prepare a list to store the car data
#     car_data = []

#     for car in cars:
#         # Extract the data from each car listing
#         url = car.find('a', class_="ListItem_title__ndA4s")['href']
#         url = 'https://www.autoscout24.es/' + url
#         location = car.find('span', class_="SellerInfo_address__leRMu")
#         if location is None:
#             location = car.find('span', class_="SellerInfo_private__THzvQ").text
#         else:
#             location = location.text

#         title_element = car.find('h2')
#         description = title_element.find('span', class_='ListItem_version__5EWfi').text.strip()
#         title = title_element.text.replace(description, '').strip()
#         brand = title.split()[0]

#         rating_elem = car.find('div', class_="scr-price-label")
#         rating = rating_elem.find('p').text
#         price = car.find('p', class_='Price_price__APlgs').text.strip()
#         price = int(re.sub(r'\D', '', price))

#         details_elements = car.find_all('span', class_='VehicleDetailTable_item__4n35N')
#         details = [detail.text.strip() for detail in details_elements]
#         mileage = details[0]
#         mileage = int(re.sub(r'\D', '', mileage))
#         transmission = details[1]
#         year = details[2]
#         # year = datetime.strptime(year, '%m/%Y')
#         engine_type = details[3]
#         cv = details[4]
#         cv = int(re.search(r'(\d+) CV', cv).group(1))

#         # Add the data to our list
#         car_data.append([brand, title, description, rating, price, mileage, transmission, year, engine_type, cv, location, url])

#     # Convert the list to a DataFrame and return it
#     return pd.DataFrame(car_data, columns=['brand', 'title', 'description', 'rating', 'full_price', 'mileage', 'transmission', 'year', 'fuel', 'cv', 'location', 'url'])


# def scrape_multiple_autoscout(base_url):
#     response = requests.get(base_url)
#     soup = BeautifulSoup(response.text, 'html.parser')

#     # Find max page 
#     page = soup.find('li', class_='pagination-item--disabled pagination-item--page-indicator')
               
#     if page is None:
#         return
#     else:
#         page= int(page.text.split()[-1])

#     # Prepare a list to store the DataFrames
#     dfs = []

#     for i in range(1, page + 1):
#         # Construct the URL for the current page
#         url = base_url + '&page=' + str(i)

#         # Scrape the current page and store the DataFrame
#         df = scrape_autoscout(url)
#         dfs.append(df)

#     # Concatenate all the DataFrames
#     master_df = pd.concat(dfs, ignore_index=True)

#     return master_df


# def scrape_flexicar(url):
#     options = webdriver.ChromeOptions()
#     prefs = {"profile.managed_default_content_settings.images": 2}
#     options.add_experimental_option("prefs", prefs)

#     driver = webdriver.Chrome(options=options)

#     driver.get(url)

#     # Scroll until seeMoreCars_button disappears
#     WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "MuiGrid-grid-sm-6")))
#     time.sleep(5)

#     container = driver.find_element(By.CLASS_NAME, "MuiGrid-spacing-xs-3")
#     number_entries = 1

#     while number_entries != len(driver.find_element(By.CLASS_NAME, "MuiGrid-spacing-xs-3").find_elements(By.CLASS_NAME, "MuiGrid-grid-sm-6")):
#         container = driver.find_element(By.CLASS_NAME, "MuiGrid-spacing-xs-3")
#         number_entries = len(container.find_elements(By.CLASS_NAME, "MuiGrid-grid-sm-6"))
#         driver.execute_script("arguments[0].scrollIntoView();", container.find_elements(By.CLASS_NAME, "MuiGrid-grid-sm-6")[-1])
#         time.sleep(0.5/number_entries)
            
#     html = driver.page_source
#     driver.quit()

#     soup = BeautifulSoup(html, 'html.parser')
#     html = soup.find('div', class_='MuiGrid-spacing-xs-3')
#     html = html.find_all('div', class_='MuiGrid-grid-sm-6' )

#     return html


# def parse_flexicars(cars):
#     cars_data = []
#     for car in cars:
#         url = car.find('a', class_='MuiLink-root')['href']
#         url = 'https://www.flexicar.es/' + url

#         title = car.find('h2', class_='MuiTypography-root').text
#         details = car.find_all('div', class_='MuiBox-root')[-2]
#         details = details.find_all('li')
#         details = [detail.text for detail in details]
#         year = int(details[0])
#         mileage = details[1]
#         mileage = int(re.sub(r'\D', '', mileage))
#         fuel = details[2]
#         transmission = details[3]

#         details = car.find_all('p', class_='MuiTypography-root')
#         details = [detail.text for detail in details]
#         location = details.pop()
#         offer = None
#         iva = None
#         if details[0][0] != 'D':
#             full_price = details.pop(0)
#             full_price = int(re.sub(r'\D', '', full_price))
#         else:
#             full_price = None
#         monthly_rate = details[0]
#         monthly_rate = int(re.sub(r'\D', '', monthly_rate))
#         description = details[1]
#         discounted_price = details[2]
#         discounted_price = int(re.sub(r'\D', '', discounted_price))
#         try:
#             if details[3] == "Oferta":
#                 offer = details[3]
#             else:
#                 iva = 'IVA Deducible'
#         except IndexError:
#             None
#         try:
#             if details[4] == "Oferta":
#                 offer = details[4]
#             else:
#                 iva = 'IVA Deducible'
#         except IndexError:
#             None
        
#         cars_data.append([title, full_price, description, discounted_price, monthly_rate, year, mileage, fuel, transmission, iva, offer, location, url])

#     df = pd.DataFrame(cars_data, columns=["title", "full_price", "description", "discounted_price", "monthly_rate", "year", "mileage", "fuel", "transmission", "iva_deducible", "offer", 'city', 'url'])

#     return df


# # Ocasionplus
# url = "https://www.ocasionplus.com/coches-ocasion/v2?orderBy=lowerPrice&kms%5Bto%5D=100000&year%5Bfrom%5D=2013&year%5Bto%5D=2022&environment=0_EMISIONES%2CC%2CECO&power%5Bfrom%5D=90&price%5Bto%5D=16000"
# df = parse_ocasion(scrape_ocasion(url))
# df['discount'] = df.apply(impute_missing, axis=1)
# df = df.drop_duplicates()
# df.to_csv(f'data/ocasion/{datetime.now().strftime("%y.%m.%d")}_ocasion_raw.csv', index=False)

# # Autoscout
# df = scrape_multiple_autoscout('https://www.autoscout24.es/lst?atype=C&cy=E&damaged_listing=exclude&desc=0&doorfrom=4&doorto=5&fregfrom=2013&kmto=100000&pe_category=1&powerfrom=82&powertype=kw&pricefrom=5000&priceto=10000&sort=price&source=homepage_search-mask&ustate=N%2CU')
# df = pd.concat([df,scrape_multiple_autoscout('https://www.autoscout24.es/lst?atype=C&cy=E&damaged_listing=exclude&desc=0&doorfrom=4&doorto=5&fregfrom=2013&kmto=100000&pe_category=1&powerfrom=82&powertype=kw&pricefrom=10000&priceto=12500&sort=price&source=homepage_search-mask&ustate=N%2CU')], ignore_index=True)
# df = pd.concat([df,scrape_multiple_autoscout('https://www.autoscout24.es/lst?atype=C&cy=E&damaged_listing=exclude&desc=1&doorfrom=4&doorto=5&fregfrom=2013&kmto=100000&pe_category=1&powerfrom=82&powertype=kw&pricefrom=10000&priceto=12500&sort=price&source=homepage_search-mask&ustate=N%2CU')], ignore_index=True)
# df = pd.concat([df,scrape_multiple_autoscout('https://www.autoscout24.es/lst?atype=C&cy=E&damaged_listing=exclude&desc=0&doorfrom=4&doorto=5&fregfrom=2013&kmto=100000&pe_category=1&powerfrom=82&powertype=kw&pricefrom=12500&priceto=15000&sort=price&source=homepage_search-mask&ustate=N%2CU')], ignore_index=True)
# df = pd.concat([df,scrape_multiple_autoscout('https://www.autoscout24.es/lst?atype=C&cy=E&damaged_listing=exclude&desc=0&doorfrom=4&doorto=5&eq=130&fregfrom=2013&kmto=100000&pe_category=1&powerfrom=82&powertype=kw&pricefrom=5000&sort=price&source=homepage_search-mask&ustate=N%2CU')], ignore_index=True)
# df = df.drop_duplicates()
# df.to_csv(f'data/autoscout/{datetime.now().strftime("%y.%m.%d")}_autoscout_raw.csv', index=False)

# # Flexicars
# cars = []
# for i in range(8):
#     url = f"https://www.flexicar.es/segunda-mano/#/distintivo/selloC/distintivo/selloE/distintivo/sello0/precio_from/{(i+8)}000/precio_to/{(i+9)}000/cv_from/80/km_to/100000/year_from/2013/year_to/2022/sortBy/price/order/ASC"
#     cars += scrape_flexicar(url)

# df = parse_flexicars(cars)
# df.to_csv(f'data/flexicar/{datetime.now().strftime("%y.%m.%d")}_flexicar_raw.csv', index=False)


# Load scraped data
df1 = pd.read_csv(f'data/autoscout/{datetime.now().strftime("%y.%m.%d")}_autoscout_raw.csv')
df1['title'] = df1['brand'] + ' ' + df1['title']
df1 = df1.drop(['brand', 'rating'], axis=1)
df1['location'] = df1['location'].str.extract(r'ES-\d+\s(.*)', expand=False)
df1['year'] = df1['year'].str.split('/').str[1].astype(int)

df2 = pd.read_csv(f'data/flexicar/{datetime.now().strftime("%y.%m.%d")}_flexicar_raw.csv')
df2['location'] = df2['city']
df2['cv'] = df2['description'].str.extract(r'\((\d+)CV\)', expand=False)
df2['cv'] = df2['cv'].replace(np.nan, '0')
df2['cv'] = df2['cv'].astype(int)
df2['cv'] = df2['cv'].replace(0, np.nan)
df2 = df2.drop(['discounted_price', 'monthly_rate', 'iva_deducible', 'offer', 'city'], axis=1)

df3 = pd.read_csv(f'data/ocasion/{datetime.now().strftime("%y.%m.%d")}_ocasion_raw.csv')
df3['city'] = df3['city'].fillna('')
df3['district'] = df3['district'].fillna('')
df3['location'] = df3['city'] + ' ' + df3['district']
df3['location'] = df3['location'].replace(' ', np.nan)
df3 = df3.drop(['discounted_price', 'discount', 'status', 'city', 'district', 'libro', 'warranty', 'owner', 'vista'], axis=1)

# Combine and prep data
df2 = df2[df1.columns]
df3 = df3[df1.columns]
df = pd.concat([df1,df2,df3], ignore_index=True)
df['location'] = df['location'].str.lower().str.strip()
df = df.drop_duplicates()
df = df.dropna(subset=['full_price'])
df['age'] = 2024 - df['year']
df = df.drop(['year'], axis=1)

df = df[df['full_price'] <= 15000]
df.drop_duplicates(subset=['title', 'description', 'full_price', 'mileage', 'transmission', 'fuel', 'cv', 'age'], inplace=True)


# Normalize
scaler = MinMaxScaler()
df_norm = df.copy()
df_norm['full_price'] = scaler.fit_transform(df_norm[['full_price']])
df_norm['age'] = scaler.fit_transform(df_norm[['age']])
df_norm['mileage'] = scaler.fit_transform(df_norm[['mileage']])
df_norm['cv'] = scaler.fit_transform(df_norm[['cv']])
df_norm['cv'] = df_norm['cv'].replace(np.nan, 0)

## Correct valence
df_norm['full_price'] = (df_norm['full_price'] - 1)* -1
df_norm['age'] = (df_norm['age'] - 1)* -1
df_norm['mileage'] = (df_norm['mileage'] - 1)* -1

df['rating'] = (df_norm.full_price * 2) + df_norm.cv + df_norm.mileage + df_norm.age
df['rating_no_cv'] = (df_norm.full_price * 2) + df_norm.mileage + df_norm.age
df['description'] = df.title + ' ' + df.description
df['title'] = df['title'].apply(lambda x: x.split(" ")[0])

df.to_csv(f'data/{datetime.now().strftime("%y.%m.%d")}_assembled.csv', index=False)