import argparse
from datetime import datetime
import json
import os
import re
import time

from urllib.request import urlopen
from urllib.error import HTTPError
import bs4
import pandas as pd
from datetime import datetime
import glob


def get_all_lists(soup):

    lists = []
    list_count_dict = {}

    if soup.find('a', text='More lists with this book...'):

        lists_url = soup.find('a', text='More lists with this book...')['href']

        source = urlopen('https://www.goodreads.com' + lists_url)
        soup = bs4.BeautifulSoup(source, 'lxml')
        lists += [' '.join(node.text.strip().split()) for node in soup.find_all('div', {'class': 'cell'})]

        i = 0
        while soup.find('a', {'class': 'next_page'}) and i <= 10:

            time.sleep(2)
            next_url = 'https://www.goodreads.com' + soup.find('a', {'class': 'next_page'})['href']
            source = urlopen(next_url)
            soup = bs4.BeautifulSoup(source, 'lxml')

            lists += [node.text for node in soup.find_all('div', {'class': 'cell'})]
            i += 1

        # Format lists text.
        for _list in lists:
            # _list_name = ' '.join(_list.split()[:-8])
            # _list_rank = int(_list.split()[-8][:-2]) 
            # _num_books_on_list = int(_list.split()[-5].replace(',', ''))
            # list_count_dict[_list_name] = _list_rank / float(_num_books_on_list)     # TODO: switch this back to raw counts
            _list_name = _list.split()[:-2][0]
            _list_count = int(_list.split()[-2].replace(',', ''))
            list_count_dict[_list_name] = _list_count

    return list_count_dict

def get_shelves(soup):

    shelf_count_dict = {}
    
    if soup.find('a', text='See top shelves…'):

        # Find shelves text.
        shelves_url = soup.find('a', text='See top shelves…')['href']
        source = urlopen('https://www.goodreads.com' + shelves_url)
        soup = bs4.BeautifulSoup(source, 'lxml')
        shelves = [' '.join(node.text.strip().split()) for node in soup.find_all('div', {'class': 'shelfStat'})]
        
        # Format shelves text.
        shelf_count_dict = {}
        for _shelf in shelves:
            _shelf_name = _shelf.split()[:-2][0]
            _shelf_count = int(_shelf.split()[-2].replace(',', ''))
            shelf_count_dict[_shelf_name] = _shelf_count

    return shelf_count_dict

def get_genres(soup):
    genre_spans = soup.find_all('span', {'class': 'BookPageMetadataSection__genreButton'})
    genres = []
    for span in genre_spans:
        genre = span.find('span', {'class': 'Button__labelItem'}).text
        if genre != '...more':
            genres.append(genre)
    return genres

def get_series_name(soup):
    series_element = soup.find('h3', {'class': 'Text Text__title3 Text__italic Text__regular Text__subdued'})
    if series_element:
        series_name = series_element['aria-label']
        return series_name
    else:
        return None

def get_series_uri(soup):
    series = soup.find(id="bookSeries").find("a")
    if series:
        series_uri = series.get("href")
        return series_uri
    else:
        return ""

def get_top_5_other_editions(soup):
    other_editions = []
    for div in soup.findAll('div', {'class': 'otherEdition'}):
      other_editions.append(div.find('a')['href'])
    return other_editions

def get_isbn(soup):
    try:
        isbn = re.findall(r'nisbn: [0-9]{10}' , str(soup))[0].split()[1]
        return isbn
    except:
        return "isbn not found"

def get_isbn13(soup):
    try:
        isbn13 = re.findall(r'nisbn13: [0-9]{13}' , str(soup))[0].split()[1]
        return isbn13
    except:
        return "isbn13 not found"

def get_rating_distribution(soup):
    rating_bars = soup.find_all('div', {'class': 'RatingsHistogram__bar'})
    distribution_dict = {}
    for bar in rating_bars:
        star_rating = bar['aria-label'].split(' ')[0]
        total_ratings = bar.find('div', {'class': 'RatingsHistogram__labelTotal'}).text
        num_ratings = total_ratings.split(' ')[0]
        num_ratings = int(num_ratings.replace(',', ''))
        distribution_dict[star_rating] = num_ratings
    return distribution_dict

def get_num_pages(soup):
    if soup.find('span', {'itemprop': 'numberOfPages'}):
        num_pages = soup.find('span', {'itemprop': 'numberOfPages'}).text.strip()
        return int(num_pages.split()[0])
    return ''

def get_year_first_published(soup):
    year_first_published = soup.find('nobr', attrs={'class':'greyText'})
    if year_first_published:
        year_first_published = year_first_published.string
        return re.search('([0-9]{3,4})', year_first_published).group(1)
    else:
        return ''

def get_id(bookid):
    pattern = re.compile("([^.-]+)")
    return int(pattern.search(bookid).group())

def get_cover_image_uri(soup):
    series = soup.find('img', id='coverImage')
    if series:
        series_uri = series.get('src')
        return series_uri
    else:
        return ""
    
def scrape_book(book_id):
    url = 'https://www.goodreads.com/book/show/' + book_id
    source = urlopen(url)
    soup = bs4.BeautifulSoup(source, 'html.parser')
    # time.sleep(1.5)

    try:
        # Extract the script tag and convert its content into a Python dictionary
        script_tag = soup.find('script', {'type': 'application/ld+json'})
        data = json.loads(script_tag.string)
    except AttributeError:
        print(f"============================= Skipping book {book_id} because the script tag was not found.")
        return None

    return {#'book_id_title':        book_id,
            'book_id':              get_id(book_id),
            #'cover_image_uri':      get_cover_image_uri(soup),
            'book_title':           ' '.join(soup.find('h1', {'class': 'Text Text__title1'}).text.split()),
            "book_series":          get_series_name(soup),
            # "book_series_uri":      get_series_uri(soup),
            # 'top_5_other_editions': get_top_5_other_editions(soup),
            # 'isbn':                 get_isbn(soup),
            # 'isbn13':               get_isbn13(soup),
            # 'year_first_published': get_year_first_published(soup),
            # 'authorlink':           soup.find('a', {'class': 'authorName'})['href'],
            # 'author':               ' '.join(soup.find('span', {'itemprop': 'name'}).text.split()),
            # 'num_pages':            get_num_pages(soup),
            'genres':               get_genres(soup),
            # 'shelves':              get_shelves(soup),
            # 'lists':                get_all_lists(soup),
            'num_ratings':          data['aggregateRating']['ratingCount'],
            'num_reviews':          data['aggregateRating']['reviewCount'],
            'average_rating':       data['aggregateRating']['ratingValue'],
            'rating_distribution':  get_rating_distribution(soup)}

def condense_books(books_directory_path):
    books = []
    # Look for all the files in the directory and if they contain "book-metadata," then load them all and condense them into a single file
    for file_name in os.listdir(books_directory_path):
        if f'_metadata.json' in file_name:
            _book = json.load(open(books_directory_path + '/' + file_name, 'r')) #, encoding='utf-8', errors='ignore'))
            books.append(_book)
    return books

def delete_metadata():
    directory = './data/*metadata.json'
    files = glob.glob(directory)
    for f in files:
        os.remove(f)

def main():

    start_time = datetime.now()
    script_name = os.path.basename(__file__)

    parser = argparse.ArgumentParser()
    parser.add_argument('--book_ids_path', type=str)
    parser.add_argument('--output_directory_path', type=str)
    parser.add_argument('--format', type=str, action="store", default="csv",
                        dest="format", choices=["csv"],
                        help="set file output format")
    args = parser.parse_args()

    current_month = start_time.strftime('%m-%Y')
    current_bookpath = args.book_ids_path + f'/book_ids.txt'

    book_ids = [line.strip() for line in open(current_bookpath, 'r', encoding='utf-8') if line.strip()]
    books_already_scraped = [file_name.replace(f'_metadata.json', '') for file_name in os.listdir(args.output_directory_path) if file_name.endswith('.json')]
    
    if os.path.isfile(f'./data/{current_month}_goodreads_scraped.csv'):
        old_df = pd.read_csv(f'./data/{current_month}_goodreads_scraped.csv')
        old_book_ids = old_df.book_id.tolist()
        old_book_ids = [str(id) for id in old_book_ids]
        print(len(old_book_ids))
        books_to_scrape = [book_id for book_id in book_ids if book_id not in old_book_ids and book_id not in books_already_scraped]
        print(len(books_to_scrape))
    else:
        books_to_scrape = [book_id for book_id in book_ids if book_id not in books_already_scraped]

    condensed_books_path   = args.output_directory_path + f'/{current_month}_goodreads_scraped'

    if books_to_scrape == []:
        delete_metadata()
        print('\nAll books already scraped\n')
    else:
        for i, book_id in enumerate(books_to_scrape):
            try:
                print(str(datetime.now()) + ' ' + script_name + ': Scraping ' + book_id + '...')
                print(str(datetime.now()) + ' ' + script_name + ': #' + str(i+1+len(books_already_scraped)) + ' out of ' + str(len(book_ids)) + ' books')

                book = scrape_book(book_id)
                if book == None:
                    continue
                else:
                    # Add book metadata to file name to be more specific
                    json.dump(book, open(args.output_directory_path + '/' + book_id + f'_metadata.json', 'w'))

                print('=============================')

            except HTTPError as e:
                print(e)
                exit(0)

        books = condense_books(args.output_directory_path)
        book_df = pd.DataFrame(books)

        if os.path.isfile(f'./data/{current_month}_goodreads_scraped.csv'):
            old_df = pd.read_csv(f'./data/{current_month}_goodreads_scraped.csv')
            book_df = pd.concat([old_df, book_df])
            book_df.to_csv(f"{condensed_books_path}.csv", index=False, encoding='utf-8')
        else:
            book_df.to_csv(f"{condensed_books_path}.csv", index=False, encoding='utf-8')
        
        delete_metadata()
        print(str(datetime.now()) + ' ' + script_name + f':\n\n🎉 Success! All book metadata scraped. 🎉\n\nMetadata files have been output to /{args.output_directory_path}\nGoodreads scraping run time = ⏰ ' + str(datetime.now() - start_time) + ' ⏰')


if __name__ == '__main__':
    main()
