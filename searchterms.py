import os
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup


# define search terms
search_terms = ['car', 'truck', 'motorcycle', 'boat', 'airplane', 'train', 'ship', 'helicopter']

# set up Chrome driver
driver_path = '/path/to/chromedriver.exe' # update with your own path
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
driver = webdriver.Chrome(driver_path, options=options)

# create directory for downloaded images
download_dir = 'downloads'
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

# create CSV file for storing image URLs
csv_file = 'image_urls.csv'
with open(csv_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['search_term', 'url'])

# loop through search terms and scrape image URLs
for search_term in search_terms:
    print(f"Searching for images of {search_term}...")
    
    # navigate to Google Images search
    driver.get('https://www.google.com/imghp')
    search_box = driver.find_element(By.NAME, 'q')
    search_box.send_keys(search_term)
    search_box.send_keys(Keys.RETURN)
    
    # scroll to bottom of page to load more images
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    
    # parse image URLs from HTML source
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    img_tags = soup.find_all('img', class_='rg_i')
    urls = [img['src'] for img in img_tags if 'http' in img['src']]
    
    # save image URLs to CSV file
    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for url in urls:
            writer.writerow([search_term, url])
    
    # download images and save to directory
    for i, url in enumerate(urls):
        try:
            response = requests.get(url, stream=True)
            with open(os.path.join(download_dir, f"{search_term}_{i}.jpg"), 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
        except:
            continue
    
