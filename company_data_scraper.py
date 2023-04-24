"""
Web Scraper to extract companies data from www.greatplacetowork.es/certificadas.

Author: Maria Dancianu
"""

from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd 
from time import sleep 


def get_url_soup(url, 
                 crawling_delay=5):
    """Opens the website and returns a BeautifulSoup object.
    
    Args:
      homepage_url: string
          URL of the website to be scraped. 
      crawling_delay: int, optional, Default = 5 
          Waiting time, in seconds, before crawling the website page. 
          This is required to avoid causing performance issues to the 
          website. 
      
    Returns: 
      soup: BeautifulSoup object
          BeautifulSoup object representing the page to be scraped. 
    """
    
    sleep(crawling_delay)

    page = urlopen(url)
    html_bytes = page.read()
    html = html_bytes.decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    
    return soup


def get_company_info(soup):
    """Extracts the main data of a single company. 
    
    Args:
      soup: BeautifulSoup object
          BeautifulSoup object representing the page to be scraped. 
          
    Returns:
      output_dict: dictionary 
          Dictionary with the company data, such as name, number of
          employees, headquarters, sector. 
    """
    
    try:
        company_details = soup.findAll('div', attrs={'class': 'uvc-sub-heading ult-responsive'})
        
        number_of_employees = company_details[0].string
        sector = company_details[1].string
        headquarters = company_details[2].string
        
        output_dict = {
            'number_of_employees': number_of_employees, 
            'sector': sector, 
            'headquarters': headquarters
         }
        
    except:
        print("Could not get the company info!")
        
        output_dict = {
            'number_of_employees': None, 
            'sector': None,
            'headquarters': None
         }
        
    return output_dict
    

def get_company_urls(soup):
    """Extracts the URLs (website and social media) of a 
    single company. 
    
    Args:
      soup: BeautifulSoup object
          BeautifulSoup object representing the page to be scraped. 
          
    Returns:
      output_dict: dictionary 
          Dictionary with the company URLs. 
    """
    
    try:
        links = soup.findAll('a', href=True, attrs={'data-toggle':'tooltip'})
        links = [l['href'] for l in links]
       
        linkedin_url = [l for l in links if 'linkedin' in l]
        twitter_url =  [l for l in links if 'twitter' in l]
        instagram_url = [l for l in links if 'instagram' in l]
        facebook_url = [l for l in links if 'facebook' in l]
        
        if len(linkedin_url) > 0:
            linkedin_url = linkedin_url[0]
        else:
            linkedin_url = None
            
        if len(twitter_url) > 0:
            twitter_url = twitter_url[0]
        else:
            twitter_url = None
            
        if len(instagram_url) > 0:
            instagram_url = instagram_url[0]
        else:
            instagram_url = None
            
        if len(facebook_url) > 0:
            facebook_url = facebook_url[0]
        else:
            facebook_url = None
        
        company_url = [l for l in links if l not in
                       [linkedin_url, twitter_url, instagram_url, facebook_url]]
        
        if len(company_url) > 0:
            company_url = company_url[0]
        else:
            company_url = None
        
        output_dict = {
            'company_website': company_url, 
            'linkedin': linkedin_url, 
            'facebook': facebook_url,
            'twitter': twitter_url,
            'instagram': instagram_url
         }     
    except:
        print("Could not get the company urls!")
        
        output_dict = {
            'company_website': None, 
            'linkedin': None, 
            'facebook': None,
            'twitter': None,
            'instagram': None
         }
    
    return output_dict


def scrape_one_company_data(company_url):
    """Extracts the data of a single company. 
    
    Args:
      company_url: string
          URL of the company website to be scraped. 
          
    Returns:
      output_dict: dictionary 
          Dictionary with the company data. 
    """
    
    output_dict = {}
    
    soup = get_url_soup(company_url)
    
    company_name = soup.find('h1', attrs={'class': 'masonry-title entry-title'}).string
   
    company_details_dict = get_company_info(soup)
    company_urls_dict = get_company_urls(soup)
    
    output_dict['name'] = company_name
    output_dict.update(company_details_dict)
    output_dict.update(company_urls_dict)
    
    return output_dict


def scrape_page_companies(soup):
    """Extract the companies data from one single page. 
    
    Args:
      soup: BeautifulSoup object
          BeautifulSoup object representing the page to be scraped. 
      
    Returns:
      page_companies_list: list
          List of dictionaries with the data of all the 
          companies of the page. 
    """
    
    page_companies_list = []
   
    all_companies = soup.find_all('article')
    
    for company in all_companies:
        company_href = company.findAll('a', href=True, attrs={'rel': 'bookmark'})
        company_url = company_href[0]['href']
        
        company_data_dict = scrape_one_company_data(company_url)
        
        page_companies_list.append(company_data_dict)
   
    return page_companies_list
    
    
    
def get_website_num_pages(homepage_url):
    """Gets the number of pages of the website.
      
    Args:
      homepage_url: string
          URL of the website to be scraped. 
    
    Returns:
      number_of_pages: int
          Number of pages of the website. 
    """
    
    soup = get_url_soup(homepage_url)

    pages = soup.find('div', attrs={'class': 'pagenav'})
    pages = pages.findAll('a', href=True)
    
    last_page_url = pages[-1]['href']
    
    number_of_pages = last_page_url.split('/')[-2]

    number_of_pages = int(number_of_pages)
    
    return number_of_pages
    
    
def get_pages_url_list(homepage_url):
    """Gets the list of all the URL pages of the website. 
    
    Args:
      homepage_url: string
          URL of the website to be scraped. 
    
    Returns:
      urls_list: list of strings
          List of all the URL pages of the website. 
    """
    
    urls_list = []

    number_of_pages = get_website_num_pages(homepage_url)
    
    for page in range(1, number_of_pages + 1):
        if page == 1:
            page_url = homepage_url
        else:
            page_url = f'{homepage_url}page/{page}/'
        
        urls_list.append(page_url)
    
    return urls_list

    
def CompaniesDataScraper():
    """Extracts companies data.
    
    Returns:
        None but saves a csv named with the extracted data.
    """
    
    all_companies_list = []
    
    homepage_url = "https://greatplacetowork.es/certificadas/"
    
    pages_url_list = get_pages_url_list(homepage_url)

    for page_url in pages_url_list:
        soup = get_url_soup(page_url)
                
        page_companies_list = scrape_page_companies(soup)
        
        all_companies_list.extend(page_companies_list)
        
    results_df = pd.DataFrame(all_companies_list)       
    results_df.to_csv("great_place_to_work_companies.csv")
    
    return results_df

   
if __name__ == '__main__':
    CompaniesDataScraper()
