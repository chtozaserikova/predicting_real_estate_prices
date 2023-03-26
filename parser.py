from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import numpy as np
import requests
import csv


class CianParser():
    def get_html(driver, url): 
        html = driver.page_source
        return html

    def get_content(html): 
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.find_all('article', class_ = '_93444fe79c--container--Povoi')
        return items
        
    def get_urls(driver):   
        urls = []
        params = ['&sort=creation_date_desc', 
                '&sort=creation_date_asc', 
                '&sort=price_object_order', 
                '&sort=total_price_desc', 
                '&sort=street_name', 
                '&sort=walking_time']
        
        for par in tqdm(range(len(params))):
            param = params[par] 
            for i in range(1,5): # было 55
                URL = driver.get(f'https://www.cian.ru/cat.php?deal_type=rent&engine_version=2&offer_type=flat&p={i}&region=1&room1=1&{param}&type=4')
                html = CianParser.get_html(driver, URL)
                items = CianParser.get_content(html)
                for item in items:
                    urls.append(item.find('a', class_='_93444fe79c--link--eoxce').get('href'))
            urls = list(set(urls))
        return urls


    def get_data(driver, urls): 
        prices, metro, floor, max_floor, size, msize, deadline, bathroom, renovation, time = [], [], [], [], [], [], [], [], [], []
        for i in tqdm(range(len(urls))):
            url = urls[i]
            driver.set_page_load_timeout(0.8)
            URL = driver.get(url)
            html = get_html(URL)
            soup = BeautifulSoup(html, 'html.parser')
            try: 
                price = soup.find('span', class_ = "a10a3f92e9--price_value--lqIK0").find('span').get('content')
                prices.append(int(price.replace(' ', '').rstrip('₽/мес.')))
            except AttributeError: prices.append(np.nan)
                
            try: metro.append(soup.find('a', class_ = 'a10a3f92e9--underground_link--Sxo7K').get_text())
            except AttributeError: metro.append(np.nan)
            
            try: time.append(int(soup.find('span', class_ = 'a10a3f92e9--underground_time--iOoHy').get_text()[4:6]))
            except AttributeError: time.append(np.nan)
            except ValueError: time.append(np.nan)
            
            block1 = soup.find_all('div', class_ = 'a10a3f92e9--info-value--bm3DC')
            titles1 = soup.find_all('div', class_ = 'a10a3f92e9--info-title--JWtIm')
            
            flag = [0,0,0,0]
            for i in range(len(titles1)):
                if titles1[i].get_text() == 'Общая':
                    flag[0] = 1
                    try: size.append(float(block1[i].get_text().rstrip('\xa0м²').replace(',','.')))
                    except ValueError: size.append(np.nan)
                elif titles1[i].get_text() == 'Жилая':
                    flag[1] = 1
                    try: msize.append(float(block1[i].get_text().rstrip('\xa0м²').replace(',','.')))
                    except ValueError: msize.append(np.nan)
                elif titles1[i].get_text() == 'Этаж':
                    flag[2] = 1
                    floors = block1[i].get_text().split(' из ')
                    floor.append(int(floors[0]))
                    max_floor.append(int(floors[1]))
                elif titles1[i].get_text() == 'Построен' or titles1[i].get_text() == 'Срок сдачи':
                    flag[3] = 1
                    deadline.append(int(block1[i].get_text()[-4:]))
            if flag[0] == 0:
                size.append(np.nan)
            if flag[1] == 0:
                msize.append(np.nan)
            if flag[2] == 0:
                floor.append(np.nan)
                max_floor.append(np.nan)
            if flag[3] == 0:
                deadline.append(np.nan)


            block2 = soup.find_all('span', class_ = 'a10a3f92e9--value--Y34zN')
            titles2 = soup.find_all('span', class_ = 'a10a3f92e9--name--x7_lt')

            flag = [0,0,0,0]
            for i in range(len(titles2)):
                if titles2[i].get_text() == 'Санузел':
                    flag[0] = 1
                    bathroom.append(block2[i].get_text())
                elif titles2[i].get_text() == 'Ремонт':
                    flag[1] = 1
                    renovation.append(block2[i].get_text())
            if flag[0] == 0:
                bathroom.append(np.nan)
            if flag[1] == 0:
                renovation.append(np.nan)
                
            
        return prices, metro, size, msize, floor, max_floor, deadline, bathroom, renovation, time


class AvitoParser:
    def get_html(driver, url, PARAMS = None): 
        html = driver.page_source
        return html
        
    def get_content_avito(driver, html): 
        # soup = BeautifulSoup(html, 'html.parser')
        requiredHtml = driver.page_source
        soup = BeautifulSoup(requiredHtml, 'html5lib')
        table=soup.findAll("div", {"class": "iva-item-root-_lk9K"})
        return table
    
    def get_urls_avito(driver):   
        urls = []
        for i in range(1,5): 
            URL = driver.get(f'https://www.avito.ru/moskva/kvartiry/sdam/na_dlitelnyy_srok-ASgBAgICAkSSA8gQ8AeQUg?f=ASgBAgECAkSSA8gQ8AeQUgFFxpoMFXsiZnJvbSI6MCwidG8iOjYwMDAwfQ&p={i}')
            html = AvitoParser.get_html(driver, URL)
            table = AvitoParser.get_content_avito(driver, html)
            for i, ad in enumerate(table):
                try:
                    div = ad.find('h3')
                    urls.append("https://avito.ru" + div.find('a', class_ = 'iva-item-titleStep-pdebR').get('href'))
                except:
                    urls.append(np.nan)
            urls = list(set(urls))
        return urls

    def get_data_avito(driver, urls): 
        prices, metro, floor, max_floor, size, bathroom, renovation, time = [], [], [], [], [], [], [], []
        for i in tqdm(range(len(urls))):
            url = urls[i]
            driver.set_page_load_timeout(0.8)
            URL = driver.get(url)
            html = AvitoParser.get_html(driver, URL)
            soup = BeautifulSoup(html, 'html.parser')
            try: 
                price = soup.find("span", {"class": "price-text-_YGDY text-text-LurtD text-size-s-BxGpL"}).text.strip('  ₽').split(' ₽')[0]
                prices.append(int(price.replace(' ', '')))
            except AttributeError: prices.append(np.nan)
                
            try:  
                metro.append(soup.find('a', class_ = 'style-item-address-georeferences-item-18pFt').get_text())
            except AttributeError: metro.append(np.nan)
            
            try: 
                time.append(int(soup.find('span', class_='geo-periodSection-bQIE4').text))
            except AttributeError: time.append(np.nan)
            
            block1 = soup.find_all('text')
            titles1 = soup.find_all('span', class_ = 'params-paramsList__item-appQw')
            
            flag = [0,0,0,0]
            for i in range(len(titles1)):
                if titles1[i].get_text() == 'Общая':
                    flag[0] = 1
                    try: size.append(float(block1[i].get_text().rstrip('\xa0м²').replace(',','.')))
                    except ValueError: size.append(np.nan)
                elif titles1[i].get_text() == 'Этаж':
                    flag[1] = 1
                    floors = block1[i].get_text().split(' из ')
                floor.append(int(floors[0]))
                max_floor.append(int(floors[1]))
            if flag[0] == 0:
                size.append(np.nan)
            if flag[1] == 0:
                max_floor.append(np.nan)

            block2 = soup.find_all('text')
            titles2 = soup.find_all('span', class_ = 'params-paramsList__item-appQw')

            flag = [0,0,0,0]
            for i in range(len(titles2)):
                if titles2[i].get_text() == 'Санузел':
                    flag[0] = 1
                    bathroom.append(block2[i].get_text())
                elif titles2[i].get_text() == 'Ремонт':
                    flag[1] = 1
                    renovation.append(block2[i].get_text())
            if flag[0] == 0:
                bathroom.append(np.nan)
            if flag[1] == 0:
                renovation.append(np.nan)
            driver.switch_to.window(driver.window_handles[1])
            
        return prices, metro, size, floor, max_floor, bathroom, renovation, time