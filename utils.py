import requests
import urllib
import pandas as pd
from requests_html import HTML
from requests_html import HTMLSession
from collections import defaultdict
from bs4 import BeautifulSoup
import colorama
from urllib.parse import urlparse, urljoin

class Query_and_Scrape(object):
    """docstring for Query_and_Scrape"""
    def __init__(self):
        super(Query_and_Scrape, self).__init__()


        # init the colorama module
        colorama.init()

        self.GREEN = colorama.Fore.GREEN
        self.GRAY = colorama.Fore.LIGHTBLACK_EX
        self.RESET = colorama.Fore.RESET
        self.YELLOW = colorama.Fore.YELLOW

        # initialize the set of links (unique links)
        self.total_internal_urls = set()
        self.total_external_urls = set()

        self.total_urls_visited = 0

        self.output_dict=defaultdict(list)

         
    def get_source(self,url):
        """Return the source code for the provided URL. 

        Args: 
            url (string): URL of the page to scrape.

        Returns:
            response (object): HTTP response object from requests_html. 
        """

        try:
            session = HTMLSession()
            response = session.get(url)
            return response

        except requests.exceptions.RequestException as e:
            print(e)


    def scrape_google(self,query):

        query = urllib.parse.quote_plus(query)
        response = self.get_source("https://www.google.co.uk/search?q=" + query)

        links = list(response.html.absolute_links)
        google_domains = ('https://www.google.', 
                          'https://google.', 
                          'https://webcache.googleusercontent.', 
                          'http://webcache.googleusercontent.', 
                          'https://policies.google.',
                          'https://support.google.',
                          'https://maps.google.',
                          'https://www.youtube.')

        for url in links[:]:
            if url.startswith(google_domains):
                links.remove(url)

        return links   


    def is_valid(self,url):
        """
        Checks whether `url` is a valid URL.
        """
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)


    def get_all_website_links(self,url,verbose=False):
        """
        Returns all URLs that is found on `url` in which it belongs to the same website
        """
        # all URLs of `url`
        urls = set()
        soup = BeautifulSoup(requests.get(url).content, "html.parser")
        for a_tag in soup.findAll("a"):
            href = a_tag.attrs.get("href")
            if href == "" or href is None:
                # href empty tag
                continue
            # join the URL if it's relative (not absolute link)
            href = urljoin(url, href)
            parsed_href = urlparse(href)
            # remove URL GET parameters, URL fragments, etc.
            href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
            if not self.is_valid(href):
                # not a valid URL
                continue
            if href in self.total_internal_urls:
                # already in the set
                continue
            if self.domain_name not in href:
                # external link
                if href not in self.total_external_urls:
                    if verbose:
                        print(f"{self.GRAY}[!] External link: {href}{self.RESET}")
                    self.total_external_urls.add(href)
                continue
            if verbose:
                print(f"{self.GREEN}[*] Internal link: {href}{self.RESET}")
            urls.add(href)
            self.total_internal_urls.add(href)
        return urls

    def crawl(self,url, max_urls=10,verbose=False):
        """
        Crawls a web page and extracts all links.
        You'll find all links in `external_urls` and `internal_urls` global set variables.
        params:
            max_urls (int): number of max urls to crawl, default is 30.
        """

        self.total_urls_visited += 1
        if verbose:
            print(f"{self.YELLOW}[*] Crawling: {url}{self.RESET}")
        links = self.get_all_website_links(url)
        for link in links:
            if self.total_urls_visited > max_urls:
                break
            self.crawl(link, max_urls=max_urls)

    def scrape_all_links(self,url,save=False):

        self.domain_name = urlparse(url).netloc


        internal_urls = set()
        external_urls = set()
        urls_visited = 0

        self.total_internal_urls=internal_urls
        self.external_urls=external_urls
        self.total_urls_visited=urls_visited

        self.crawl(url)


        print("[+] Total Internal links:", len(self.total_internal_urls))
        print("[+] Total External links:", len(self.total_external_urls))
        print("[+] Total URLs:", len(self.total_external_urls) + len(self.total_internal_urls))

        return list(self.total_internal_urls),list(self.total_external_urls)

    def get_website_text(self,urls):

        text_dict=defaultdict(list)
        for url in urls:
            text_dict['link'].append(url)
            self.output_dict['link'].append(url)
            html_content = requests.get(url).text
            soup = BeautifulSoup(html_content, "html.parser")
            tags=[tag.name for tag in soup.find_all()]

            for tag in tags:
                if tag=="style":
                    continue
                self.output_dict[tag].append(soup.find(tag).text)
                text_dict[tag].append(soup.find(tag).text)

        df=pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in text_dict.items() ]))

        return df

    def get_all_website_text(self):

        df=pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in self.output_dict.items() ]))

        return df