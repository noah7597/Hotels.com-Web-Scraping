from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import csv
import time

def get_url(city, state, country, checkin_date, checkout_date):
    template = 'https://www.hotels.com/search.do?&q-destination={},%20{},%20{}&q-check-in={}&q-check-out={}&q-rooms=1&q-room-0-adults=1&q-room-0-children=0&sort-order=BEST_SELLER&modal=oc'
    city = city.replace(' ', '%20')
    state = state.replace(' ', '%20')
    country = country.replace(' ','%20')
    
    url = template.format(city, state, country, checkin_date, checkout_date)
    
    return template.format(city, state, country, checkin_date, checkout_date)

def extract_record(item, image):
    
    try:
        name = item.find('h2',{'class':'_3zH0kn'}).text
    except AttributeError:
        return
    
    try:
        address = item.find('p',{'class':'_2oHhXM'}).text
    except:
        address = ''
    
    try:
        price = item.find('span',{'class':'_2R4dw5'}).text
    except:
        price = ''
        
    try:
        old_price_parent = item.find('span',{'class':'_1IxsXN _2VINEh b3TRQj'})
        old_price = old_price_parent.find('span',{'class':'k3LKyj'}).text
    except:
        old_price = ''
        
    try:    
        rating = item.find('span',{'class':'_1biq31'}).text
        
        rating = rating[:3]
    except:
        rating = ''
        
    try:
        reviews = item.find('span',{'class':'_2YwCpK'}).text
        reviews = reviews.replace(' Hotels.com guest reviews','')
    except:
        reviews = ''
        
    try:
        total_cost = item.find('span',{'class':'_2wKxGq myofY3 _3SEj8y'}).text
        total_cost = total_cost.replace('\ue965','').replace('total ','').replace('\xa0nights','')
        total_cost = total_cost.split()
        total_cost = total_cost[0]
    except:
        total_cost = ''
        
    try:
        image_src = image.get_attribute('src')
    except:
        image_src = ''
    
    result = (name, address, price, old_price, rating, reviews, total_cost, image_src)
    
    return result

def main(city, state, country, checkin_date, checkout_date, pages):
    driver = webdriver.Chrome(executable_path ="/Applications/chromedriver89")
    
    records = []
        
    driver.get(get_url('New York City', 'New York', 'United States of America', '2021-06-01', '2021-06-23'))
    
    for page in range(1, pages+1):
        
        element_present = EC.presence_of_element_located((By.XPATH, "//*[@id=" + str(page-1) + "]/div/div"))
        WebDriverWait(driver, 10).until(element_present)
        
        element = driver.find_element_by_xpath("//*[@id=" + str(page-1) + "]/div/div")
        loc = element.location
        driver.execute_script("window.scrollTo(0," + str(loc['y']) + ");")
        time.sleep(1)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        results = soup.find_all('div',{'class':'-RcIiD'})
        
        record = extract_record(results[page-1])
        if record:
            records.append(record)
    
    with open('/Users/noahhallberg/Desktop/WebScraping/Hotels.com/hotels.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'Address', 'Price', 'Normal Price', 'Rating','Reviews', 'Total Cost', 'Image'])
        writer.writerows(records)
