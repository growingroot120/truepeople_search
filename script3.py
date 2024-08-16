import os
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException

# Function to scrape profile URLs from a given URL
def scrape_profile_urls(driver, url):
    driver.get(url)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    profile_urls = []
    
    # Find all relevant div elements containing the links
    content_divs = soup.find_all('div', class_='col text-center')
    
    # Loop through each div element to find links
    for content_div in content_divs:
        profile_links = content_div.find_all('a', class_='btn btn-success btn-lg shadow-form link-to-more', href=True)
        for profile_link in profile_links:
            profile_url = profile_link['href']
            profile_urls.append(f"https://www.truepeoplesearch.com{profile_url}")
            print(f"URL scraped: {profile_urls[-1]}")
    
    return profile_urls

# Function to open or close Chrome with a given URL
def open_and_close_chrome_with_url(url, driver):
    driver.get(url)

# Main function
def main():
    try:
        # Create or append to 3.csv
        profile_urls_csv = "3.csv"
        if not os.path.exists(profile_urls_csv):
            with open(profile_urls_csv, 'w') as f:
                f.write("URL\n")  # Write header

        # Read URLs from 2.csv
        final_df = pd.read_csv("2.csv")
        urls_list = final_df['URL'].tolist()

        # Counter to keep track of processed URLs
        url_counter = 0

        # Initialize Chrome driver for the first URL
        service = Service(ChromeDriverManager().install())
        chrome_options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(service=service, options=chrome_options)
        try:
            for url in urls_list:
                # Increment URL counter
                url_counter += 1

                # Open a new Chrome instance after every 30 URLs
                if url_counter % 10 == 1:
                    if url_counter != 1:
                        driver.quit()  # Close previous Chrome instance
                    service = Service(ChromeDriverManager().install())
                    chrome_options = webdriver.ChromeOptions()
                    driver = webdriver.Chrome(service=service, options=chrome_options)
                
                print(f"Scraping profile URL from: {url}")
                profile_urls = scrape_profile_urls(driver, url)

                # Append profile URLs to profile_urls.csv
                with open(profile_urls_csv, 'a') as f:
                    for profile_url in profile_urls:
                        f.write(f"{profile_url}\n")

                # Print profile URLs
                if profile_urls:
                    print("Profile URL:")
                    for profile_url in profile_urls:
                        print(profile_url)
                else:
                    print("No profile URL found.")

        finally:
            # Close the browser after processing all URLs
            driver.quit()

        print(f"Profile URLs saved in {profile_urls_csv}")

    except WebDriverException as e:
        print(f"WebDriverException occurred: {e}")

if __name__ == "__main__":
    main()
