import os
from typing import Generator
import requests
from bs4 import BeautifulSoup, ResultSet
import string
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

# URLs to get books from
URL_EPIC = 'https://wolnelektury.pl/katalog/rodzaj/epika/'
URL_TXT = 'https://wolnelektury.pl/media/book/txt/'



# characters that are allowed in book
TEXT_FILTER = string.ascii_letters + string.digits + ' .,?!' + 'ąęćłńóśźżĄĘĆŁŃÓŚŹŻ'

# number of lines to remove from the end of the book
LINES_TO_REMOVE = 5

# amount of books to generate
BOOK_AMOUNT = int(os.environ.get('BOOK_AMOUNT', 5))
# minimum number of words per sentence
WORDS_PER_LINE = int(os.environ.get('WORDS_PER_LINE', 5))
# minimum number of lines in book for book to be added
DISCARD_LINES_THRESHOLD = int(os.environ.get('DISCARD_LINES_THRESHOLD', 300))
# overwrite existing books
SKIP_ALREADY_ADDED = os.environ.get('SKIP_ALREADY_ADDED', '1') == '1'
# name of directory to save books in
BOOKS_DIRNAME = os.environ.get('BOOKS_DIRNAME', 'books')


# create directory for books
def create_book_directory(dirname=BOOKS_DIRNAME):
    if not os.path.exists(dirname):
        logging.info('Creating directory ' + dirname)

        os.makedirs(dirname)


# get links to books
def get_book_links(url: str) -> Generator[str, None, None]:
    logging.info('Getting book links from ' + url)

    # get the HTML content
    r = requests.get(url)

    # parse the HTML content
    soup = BeautifulSoup(r.content, 'html.parser')

    # get links to books
    links: ResultSet[str] = soup.find_all('h2', class_='s')

    # yield links
    for link in links:
        yield link.a['href'].split('/')[-2]


# get txt file of the book
def get_book_txt(url_to_txt: str, book_link: str):
    return requests.get(url_to_txt + book_link + '.txt')


# save book to file
def save_book_to_file(filename: str, content: str):
    with open(filename, 'wb') as f:
        f.write(content.encode('utf-8'))


def transform_content(content: str):
    # make one sentence per line with . ? ! as end of sentence
    content = content.replace('. ', '.\n')
    content = content.replace('! ', '!\n')
    content = content.replace('? ', '?\n')

    # remove sentences that have characters not belonging to TEXT_FILTER
    content = '\n'.join(
        [line for line in content.split('\n') if all(c in TEXT_FILTER for c in line)])

    # remove empty lines
    content = '\n'.join([line for line in content.split('\n') if line])

    # in every line, remove sentences that have less than WORDS_PER_LINE words
    content = '\n'.join([line for line in content.split('\n') if len(
        line.split(' ')) >= WORDS_PER_LINE])

    # remove last 5 lines
    content = '\n'.join(content.split('\n')[:-LINES_TO_REMOVE])

    # make first letter of every sentence uppercase
    content = '\n'.join([line[0].upper() + line[1:] for line in content.split('\n')])

    # remove lines that ends with words shorter than two characters (probably abbreviations)
    content = '\n'.join([line for line in content.split('\n') if len(line.split(' ')[-1]) > 2])

    # remove lines that ends with word which contains dot not as end of sentence
    content = '\n'.join([line for line in content.split('\n') if '.' not in line.split(' ')[-1][:-1]])

    return content


def main():
    create_book_directory()
    links = get_book_links(URL_EPIC)

    books_added_count = 0

    for book_link in links:
        # break if BOOK_AMOUNT books were added
        if books_added_count == BOOK_AMOUNT:
            break
        
        # skip if book already exists
        if SKIP_ALREADY_ADDED and os.path.exists(BOOKS_DIRNAME + '/' + book_link + '.txt'):
            logging.info('Skipping:' + book_link + '.txt')
            continue

        logging.info('Adding:' + book_link + '.txt')

        # get book txt request
        r = get_book_txt(URL_TXT, book_link)

        # check if request returned 404, if so, skip
        if r.status_code == 404:
            logging.warning('404:' + book_link + '.txt')
            continue

        # get content
        content = r.content.decode('utf-8')

        # transform content
        transformed_content = transform_content(content)

        # skip if transformed content is too short
        if len(transformed_content.split('\n')) < DISCARD_LINES_THRESHOLD:
            logging.warning('Discarded:' + book_link + '.txt')
            continue

        # save to file
        save_book_to_file(
            BOOKS_DIRNAME + '/' + book_link + '.txt', transformed_content)
        
        books_added_count += 1
    
    logging.info('Added:' + str(books_added_count) + ' books')


if __name__ == '__main__':
    main()
