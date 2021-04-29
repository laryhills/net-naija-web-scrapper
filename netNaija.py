#!/usr/bin/env python
# coding: utf-8

# In[75]:


from selenium import webdriver
import time
from datetime import date
import requests
from bs4 import BeautifulSoup

import os
from selenium.webdriver.chrome.options import Options

import urllib3
import shutil

import pandas


""" TODO
    Crawl pages with driver with 10 seconds delay
        Each movie
        get movie upload date
            use soup to get each movie details
            get movie titles exclude Thai, Chinese, Korean, Portuguese, Turkish, Spanish, Vietnamese, Indonesian, Frech
            get movie download links
            get movie
            save pictures to movie images folder
            use another for imdb*******
        
    Name csv file with date
"""
print("Get Latest Movies from NetNaija")

today = date.today().strftime("%d %B %Y")


base_url = "https://www.thenetnaija.com/videos/movies/page/"

page_last = 4

list_of_movies = [] #to store results

base_dir = os.getcwd()+'/Movie List/'
dir_name = 'Net Naija'
dir_path = os.path.join(base_dir,dir_name)+' '+today+'/'
if not os.path.exists(dir_path):
    os.makedirs(dir_path)

#loop through pages
for page in range(1,page_last):
    
    chrome_options = Options()
    #chrome_options.add_argument("--headless")
    chrome_options.add_argument("window-size=400,400")
    driver = webdriver.Chrome(options=chrome_options)      
    
    temp_url = (base_url+str(page))
    
    print('Getting Info From '+temp_url)
    driver.get(temp_url)

    page_html = driver.page_source
    page_soup = BeautifulSoup(page_html, "html.parser")

    all_movies = page_soup.find_all("article",{"class":"file-one shadow"})
    for movie in all_movies:
        dic = {} 
        excludedLang= ['Thai', 'Chinese', 'Korean', 'Portuguese', 'Turkish', 'Spanish', 'Vietnamese', 'Indonesian', 'French', 'Indian', 'Japanese']
        try:
            movie = movie.find("h2")
            movie_title = movie.text
        except:
            continue
            movie_title = ""
        if any(exLang in movie_title for exLang in excludedLang):
            continue
        else:
            dic["Title"] = movie_title
            movie_url = movie.find('a')['href']      
            try:
                m_r = requests.get(movie_url, headers={'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'})
                m_c = m_r.content
                m_soup = BeautifulSoup(m_c, "html.parser")            
                movie_details = m_soup.find('blockquote',{'class':'quote-content'})
                movie_img_url = m_soup.find('img',{'title':movie_title})['src']
                try:
                    c = urllib3.PoolManager()
                    if not os.path.exists(dir_path+'/'+movie_title+'.jpg'):
                        with c.request('GET',movie_img_url, preload_content=False) as resp, open(dir_path+'/'+movie_title+'.jpg', 'wb') as out_file:
                            shutil.copyfileobj(resp, out_file)
                        resp.release_conn() 
                except e as Exception:
                    print(e)
                try:
                    dic["Genre"] = movie_details.find_all('p')[1].text.replace('Genre:','')
                except:
                    dic["Genre"] = None
                try:
                    dic["Release Date"] = movie_details.find_all('p')[2].text.replace('Release Date:','')
                except:
                    dic["Release Date"] = None
                try:
                    dic["Quality"] = movie_details.find_all('p')[4].text.replace('Source:','')
                except:
                    dic["Quality"] = None
                try:
                    imdb_url = movie_details.find_all('p')[7].text.replace('IMDB:','')
                    imdb_r = requests.get(imdb_url, headers={'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'})
                    imdb_c = imdb_r.content
                    imdb_soup = BeautifulSoup(imdb_c, "html.parser") 
                    dic["IMDB"] = imdb_soup.find('span',{'itemprop':'ratingValue'}).text
                except:               
                    dic["IMDB"] = None
                download_links = m_soup.find_all('a',{'class' : 'button download'})
                try:
                    dic["Download Link"] = download_links[1]['href']
                except:
                    dic["Download Link"] = None
                try:
                    dic["Subtitle Link"] = download_links[2]['href']
                except:
                    dic["Subtitle Link"] = None
            except:
                continue
        print('Added '+movie_title)
        list_of_movies.append(dic)         
    time.sleep(10)
    driver.quit()
    
# time.sleep(10)
    
print('Creating CSV File....')    
df = pandas.DataFrame(list_of_movies)
df = df.sort_values(by=['IMDB'], ascending=False)
cols = ['Title','Genre','Release Date','Quality','IMDB','Download Link','Subtitle Link']
df = df[cols] #reorder
df = df.reset_index(drop=True)
df.index += 1


filename = "Latest Movies From Net Naija as at "+str(today)+".csv"
df.to_csv(dir_path+'/'+filename)
print(filename+' created')    

