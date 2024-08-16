# import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from pymongo import MongoClient
import re

# MongoDB connection
client = MongoClient("mongodb+srv://work:work123@cluster0.tvtl9md.mongodb.net/")
db = client["IS"]
collection = db["ISSS"]

# Function to scrape data from a single URL
def scrape_data(url, driver):
    try:
        print(f"Scraping data from URL: {url}")
        driver.get(url)
        # time.sleep(1)  # Add a short delay to ensure the page is fully loaded

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # Scraping name
        name_element = soup.find('h1', class_='oh1')
        name = name_element.text.strip() if name_element else 'N/A'

        # Find the span containing age and date of birth information
        age_dob_element = soup.find('span', string=re.compile(r'Age \d+, Born'))
        age_and_dob = age_dob_element.text.strip() if age_dob_element else 'N/A'
        
        street_address_element = soup.find('span', itemprop='streetAddress')
        street_address = street_address_element.text.strip() if street_address_element else 'N/A'

        locality_element = soup.find('span', itemprop='addressLocality')
        locality = locality_element.text.strip() if locality_element else 'N/A'

        region_element = soup.find('span', itemprop='addressRegion')
        region = region_element.text.strip() if region_element else 'N/A'

        postal_code_element = soup.find('span', itemprop='postalCode')
        postal_code = postal_code_element.text.strip() if postal_code_element else 'N/A'

        # Initialize lists to store phone details
        phone_numbers = []
        line_types = []
        carriers = []

        # Select phone elements excluding the first two
        phone_elements = soup.select('span[itemprop="telephone"]')[2:8]  # Exclude first two phone numbers

        # Loop through phone elements and extract details
        for index, phone_element in enumerate(phone_elements):
            phone_number = phone_element.text.strip()
            parent_div = phone_element.find_parent('div', class_='col-12 col-md-6 mb-3')
            if parent_div:
                carrier_span = parent_div.find('span', class_='dt-sb')
                if carrier_span and ("Last reported" in carrier_span.text or "Possible Primary Phone" in carrier_span.text):
                    carrier_element = carrier_span.find_next_sibling('span', class_='dt-sb')
                    carrier = carrier_element.text.strip() if carrier_element else 'N/A'  # Extract carrier text
                else:
                    carrier = carrier_span.text.strip() if carrier_span else 'N/A'  # Extract carrier text
                line_type = parent_div.find('span', class_='smaller').text.strip()
            else:
                line_type = 'N/A'
                carrier = 'N/A'
            phone_numbers.append(phone_number)
            line_types.append(line_type)
            carriers.append(carrier)


        # Scraping email addresses
        email_addresses = [email.text.strip() for email in soup.select('.row.pl-sm-2 div.col') if '@' in email.text.strip()]

        # # Scraping additional details
        details_div = soup.find('div', class_='row pl-sm-2 mt-2')
        div_values_with_br = []

        if details_div:
            for row in details_div.find_all('div', class_='col-6 col-md-3 mb-2'):
                div_text = row.get_text(strip=True)
                br_text = ', '.join([b.get_text(strip=True) for b in row.find_all('b')])
                div_values_with_br.append((div_text, br_text))

        additional_details = {div_value: br_value for div_value, br_value in div_values_with_br}

        data = {
            'Name': name,
            'Age and Date of Birth': age_and_dob,
            'Address': {
                'Street': street_address,
                'Locality': locality,
                'Region': region,
                'Postal Code': postal_code
            },
            'Phone Numbers': phone_numbers,
            'Line Types': line_types,
            'Carriers': carriers,
            'Email Addresses': email_addresses,
            'Additional Details': additional_details
        }

        # Save data to MongoDB
        collection.insert_one(data)
        print(f"Data scraped and saved to MongoDB for URL: {url}")

    except Exception as e:
        print(f"Error occurred while scraping URL {url}: {e}")

def main():
    # Read URLs from final.csv
    final_df = pd.read_csv("3.csv")
    urls_list = final_df['URL'].tolist()

    try:
        # Set up Chrome browser
        service = Service(ChromeDriverManager().install())
        chrome_options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(service=service, options=chrome_options)

        url_counter = 0
        for url in urls_list:
            scrape_data(url, driver)
            url_counter += 1
            if url_counter % 10 == 0:
                # Close the browser after processing 35 URLs
                driver.quit()
                print("Chrome browser closed.")
                # Reinitialize Chrome browser
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the browser at the end
        driver.quit()
        print("Chrome browser closed.")

if __name__ == "__main__":
    main()