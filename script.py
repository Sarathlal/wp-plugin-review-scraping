#Scraping WordPress Plugin reviews using Python
#
#Here is the code snippet that useful to scrap all review content of a plugin. I think, the code is self explantory.
#
from bs4 import BeautifulSoup
from datetime import date
from os.path import exists
import requests
import re
import csv

# https://wordpress.org/plugins/vaultpress/
#https://wordpress.org/plugins/woocommerce-shipstation-integration/

plugin_slug = "vaultpress"

headers={'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15'}

def main():
    for y in range(1, 6):
        print("---------------------")
        print("Collecting " + str(y) + " star reviews")
        first_page_url="https://wordpress.org/support/plugin/" + plugin_slug + "/reviews?filter=" + str(y)
        soup = prepare_soup(first_page_url)

        page_nums = prepare_page_nums(soup)

        if page_nums:
            # For the reviews in first page
            print("Collecting reviews in page 1")
            links = prepare_review_links(soup)
            reviews = read_reviews(links)
            save_reviews(reviews, y)

            max_page_num = max(page_nums)
            for x in range(2, max_page_num + 1):
                print("Collecting reviews in page " + str(x))
                paginated_page_url = "https://wordpress.org/support/plugin/" + plugin_slug + "/reviews/page/" + str(x) + "/?filter=" + str(y)
                soup = prepare_soup(paginated_page_url)

                links = prepare_review_links(soup)
                reviews = read_reviews(links)
                save_reviews(reviews, y)
                
        else:
            print("Collecting reviews in page 1")
            links = prepare_review_links(soup)
            reviews = read_reviews(links)
            save_reviews(reviews, y)

def prepare_soup(url):
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup

def prepare_page_nums(soup):
    pagination_links = soup.find('div',attrs={'class':'bbp-pagination-links'})
    page_nums = []
    if pagination_links is not None:
        for pagination_link in pagination_links:
            page_num = pagination_link.text.strip()
            if page_num:
                matched=re.search("[^\d]",page_num)
                if matched==None:
                    page_nums.append(int(page_num))
    return page_nums

def prepare_review_links(soup):
    links = [link['href'] for link in soup.findAll('a',attrs={'class':'bbp-topic-permalink'})]
    return links

def read_reviews(links):
    reviews = []
    for link in links:
        review_row = []
        page = requests.get(link, headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        review_title_wrap = soup.find('header',attrs={'class':'page-header'})
        review_content = soup.find('div',attrs={'class':'bbp-topic-content'})
        if review_content.find('ul',attrs={'class':'bbp-topic-revision-log'}):
            review_content.find('ul',attrs={'class':'bbp-topic-revision-log'}).clear()
        review_date_wrap = soup.find('p',attrs={'class':'bbp-topic-post-date'})
        review_row.append(review_title_wrap.h1.text)
        review_row.append(review_content.text)
        review_date = review_date_wrap.a['title']
        review_row.append(review_date)
        review_row.append(link)
        reviews.append(review_row)
    return reviews

def save_reviews(reviews, star):
    file_name = str(date.today()) + "_" + plugin_slug + "_" + str(star) + "_star.csv"
    if not exists(file_name):
        fp = open(file_name, 'x')
        fp.close()
        print("new file created - " + file_name)

    # opening the csv file in 'w+' mode
    file = open(file_name, 'a', newline ='')

    with file:   
        write = csv.writer(file)
        write.writerows(reviews)

main()
