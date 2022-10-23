import requests
from bs4 import BeautifulSoup
from autoscraper import AutoScraper
from collections import defaultdict
import pandas as pd
from utils import Query_and_Scrape
import argparse

def main(query):

	qas=Query_and_Scrape()
	top_searches=qas.scrape_google(query)
	for search in top_searches:
		print("google search link :",search)
		internal_links,external_links=qas.scrape_all_links(search)
		internal_df=qas.get_website_text(internal_links)


	combined_df=qas.get_all_website_text()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Link and HTML extractor Tool with Python")
    parser.add_argument("query", help="The query to search on google for.")

    args = parser.parse_args()
    query = args.query
    main(query)
