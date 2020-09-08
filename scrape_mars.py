# Dependencies
from splinter import Browser
from bs4 import BeautifulSoup as bs
import datetime as dt
import pandas as pd
import requests
import time


def home():
    executable_path = {'executable_path': 'chromedriver.exe'}
    return Browser('chrome', **executable_path, headless=False)


def scrape():
    browser = home()

    news_title, news_p = html_news()

    data = {
        "news_title": news_title,
        "news_paragraph": news_p,
        "featured_image": featured_image_url(),
        "facts": mars_url(),
        "hemispheres": hemisphere_url(),
       
    }
    browser.quit()
    return data 



def html_news():
    browser = home()
    nasa_url = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'
    browser.visit(nasa_url)

    html_news = browser.html

    #Parse the website HTML with beautifulSoup
    soup_news = bs(html_news, 'html.parser')

    try:
        #Find the element
        slideElement = soup_news.select_one('ul.item_list li.slide')
        #slideElement
        slideElement.find("div", class_='content_title').get_text()

        news_title = slideElement.find("div", class_='content_title').get_text()

        news_p = slideElement.find("div", class_ = 'article_teaser_body').get_text()

    except AttributeError:
        return None, None
    
    browser.quit()
    return news_title, news_p


def featured_image_url():
    browser = home()

    # Scrapping JPL Mars Space Images 
    jpl_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(jpl_url)

    full_image = browser.find_by_id("full_image")
    full_image.click()

    browser.is_element_present_by_text("more info", wait_time=1)
    more_info_element = browser.find_link_by_partial_text("more info")
    more_info_element.click()

    html_jpl = browser.html
    soup_jpl = bs(html_jpl, 'html.parser')

    featured_image_url = soup_jpl.select_one("figure.lede a img")
    try:
        featured_image_url1 = featured_image_url.get("src")
    except AttributeError:
        return None
    featured_image_url1 = f'https://www.jpl.nasa.gov{featured_image_url1}'
    
    browser.quit()
    return featured_image_url1

def mars_url():
    browser = home()
    #Use pandas to scrape table 
    mars_url = pd.read_html("https://space-facts.com/mars/")[0]
  
   
    #Rename columns 
    mars_url.columns=['Description', 'Value']
    mars_url.set_index('Description', inplace=True)
    

    mars_url.to_html('mars_url.html')
    #Convert data to HTML table string
    mars_url_facts = mars_url.to_html(header=True, index=True)
 
    browser.quit()
    return mars_url_facts



def hemisphere_url():
    browser = home()
    hemisphere_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(hemisphere_url)

    hemisphere_list = []

    all_links_url = browser.find_by_css("a.product-item h3")
    for x in range(len(all_links_url)):
        hemi = {}
    
        #find element in each loop 
        browser.find_by_css("a.product-item h3")[x].click()
        
        #find sample tag and extract href 
        sample_tag = browser.find_link_by_text("Sample").first
        hemi["img_url"] = sample_tag["href"]
        
        #extract title 
        hemi["title"] = browser.find_by_css("h2.title").text
        
        #append object to list 
        hemisphere_list.append(hemi)
        
    browser.quit()
    return hemisphere_list
