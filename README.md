# Book Scraper

Python script used for scraping books content from legal source - [https://wolnelektury.pl/](https://wolnelektury.pl/). Content of books is used for training machine learning models.

## Prerequisites

- Python 3.11 or higher

## Usage

1. Clone the repository

```bash
git clone https://github.com/korekcjoner/book-scraper
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Create `.env` file

```bash
cp .env.example .env
```

4. Edit `.env` file in your favorite editor (e.g. vim) to your liking

```bash
vim .env
```

5. Run the script

```bash
python main.py
```

6. Books are saved in `books` directory

```bash
ls books
```

## License

[MIT](https://choosealicense.com/licenses/mit/)
