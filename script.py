#Scraping WordPress Plugin reviews using Python
#
#Here is the code snippet that useful to scrap all review content of a plugin. I think, the code is self explantory.
#
from bs4 import BeautifulSoup
import requests
import re
from datetime import date

# https://wordpress.org/plugins/vaultpress/
#https://wordpress.org/plugins/woocommerce-shipstation-integration/

plugin_slug = "woocommerce-shipstation-integration"

headers={'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15'}

def main():
    for y in range(1, 6):
        print(y)
        first_page_url="https://wordpress.org/support/plugin/" + plugin_slug + "/reviews?filter=" + str(y)
        soup = prepare_soup(first_page_url)

        page_nums = prepare_page_nums(soup)

        if page_nums:
            # For the reviews in first page
            links = prepare_review_links(soup)
            reviews = read_reviews(links)
            print(reviews)

            max_page_num = max(page_nums)
            for x in range(2, max_page_num + 1):
                paginated_page_url = "https://wordpress.org/support/plugin/" + plugin_slug + "/reviews/page/" + str(x) + "/?filter=" + str(y)
                soup = prepare_soup(paginated_page_url)

                links = prepare_review_links(soup)
                reviews = read_reviews(links)
                print(reviews)
        else:
            links = prepare_review_links(soup)
            reviews = read_reviews(links)
            print(reviews)
            save_reviews(reviews, y)

def prepare_soup(url):
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup

def prepare_page_nums(soup):
    pagination_links = soup.find('div',attrs={'class':'bbp-pagination-links'})
    page_nums = []
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
    print('save_reviews')
    print(date.today())
    print(reviews)
    print(star)
    
    

main()
