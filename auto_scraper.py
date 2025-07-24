from bs4 import BeautifulSoup
import time
import requests
import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# header <h2 data-cmp="subheading" class="text-bold text-size-400 link-unstyled" role="heading" aria-level="3">Certified 2024 Toyota Highlander XLE</h2>
# mileage <div class="text-bold text-subdued-lighter margin-top-3" data-cmp="mileageSpecification">18,383 miles</div>
# price <div class="text-size-500 text-ultra-bold first-price" data-cmp="firstPrice">42,491</div>

def get_page(url):
    options = Options()
    #options.add_argument("--headless")  # Runs browser in background
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # Wait until listings are present (adjust timeout if needed)
    try:
        WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-cmp="subheading"]'))
        )
    except Exception as e:
        print("Timeout or issue loading listings:", e)

    # Get full rendered HTML
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()
    return soup






def generate_url(trim="limited", mileage=40000, start_year=2023):
    base_url = "https://www.autotrader.com/cars-for-sale/toyota/highlander"
    city = "raleigh-nc"

    url = f"{base_url}/{trim}/{city}?mileage={mileage}&searchRadius=500&startYear={start_year}"
    return url


def extract_listings(soup):
    # Extract all matching elements
    headers = soup.find_all("h2", {"data-cmp": "subheading"})
    mileages = soup.find_all("div", {"data-cmp": "mileageSpecification"})
    prices = soup.find_all("div", {"data-cmp": "firstPrice"})

    listings = []

    for i in range(min(len(headers), len(mileages), len(prices))):
        title = headers[i].get_text(strip=True)
        mileage = mileages[i].get_text(strip=True)
        price = prices[i].get_text(strip=True)
        parsed_title = parse_title(title)
        # print(parsed_title)


        listings.append({
            "id" : i,
            **parsed_title,
            "mileage": mileage,
            "price": price
        })

    return listings


def parse_title(title):
    # Case-insensitive match for Certified
    certified = "certified" in title.lower()

    # Extract 4-digit year starting with 20
    year_match = re.search(r"\b(20\d{2})\b", title)
    year = year_match.group(1) if year_match else None

    # Look for trims — Limited or Premium
    trim = None
    for t in ["Limited", "Premium"]:
        if t.lower() in title.lower():
            trim = t
            break

    return {
        #"title": title,
        "year": year,
        "trim": trim,
        "certified": certified

    }

def get_all_listings():
    all_listings = []

    for trim in ["limited", "platinum"]:
        url = generate_url(trim)
        print(f"Fetching: {url}")
        soup = get_page(url)
        listings = extract_listings(soup)
        all_listings.extend(listings)

    return all_listings




if __name__ == "__main__":
    print("Run")
    listings = get_all_listings()
    print(listings)


