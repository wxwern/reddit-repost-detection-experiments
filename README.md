# arp-thingy
# :D


## Installation and usage
Set up the virtual environment using python 3.8
```
virtualenv -p python3.8 venv
```
You may need to replace that with the absolute path to python3.8 if you don't have that in your PATH.

To enter this project's virtual environment via the command line, enter:
- on macOS/Linux: `source venv/bin/activate`
- on Windows: `venv/Scripts/activate.bat`

After entering the virtual environment, install the latest version of `pip`, and then `requirements.txt`:
```
pip install --upgrade pip
pip install -r requirements.txt
```

To exit the virtual environment, run `deactivate`.

## Usage

You should use the following under your virtual environment if you installed it that way.

To scrape meme images from reddit, use:
```
python reddit/scraper.py
```

To use the repost checker and other related tools on the scraped contents, run:
```
python -i repost_tools.py
```

Useful scripts for repost generation and performance benchmarking:
```
python repost_generate.py
python repost_generate_jsons.py
python repost_benchmark.py
python repost_benchmark_jsons.py
```

## Comments/Complaints
`pipenv` is broken so we're migrating to barebones `virtualenv` and `requirements.txt`
