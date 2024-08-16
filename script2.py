import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException
import os

def scrape_urls(driver, base_url, max_pages):
    try:
        driver.get(base_url)

        all_urls = []

        base_url_without_page = base_url.rsplit('/', 1)[0]  # Remove the page number from the base URL

        for current_page in range(1, max_pages + 1):
            page_url = f"{base_url_without_page}/{current_page}"
            driver.get(page_url)

            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            div_tags = soup.find_all('div', class_='col-6 col-md-3')
            urls = [f"https://www.truepeoplesearch.com{div.find('a')['href']}" for div in div_tags]
            all_urls.extend(urls)

        return all_urls

    except WebDriverException as e:
        print(f"WebDriverException occurred: {e}")
        return []
    except Exception as e:
        print(f"Other Exception occurred: {e}")
        return []

def main():
    # Initialize an empty DataFrame and save it as a CSV file
    final_df = pd.DataFrame(columns=['URL'])
    final_csv = "2.csv"
    final_df.to_csv(final_csv, index=False)
    print(f"Empty CSV file generated: {final_csv}")

    # Read URLs from urls.csv
    urls_df = pd.read_csv("1.csv")
    urls_list = urls_df['URL'].tolist()

    # Scrape URLs and add to the DataFrame
    for url in urls_list:
        # Initialize Chrome driver for each URL
        service = Service(ChromeDriverManager().install())
        chrome_options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(service=service, options=chrome_options)
        # from here you can change the pages..... i made 2 for right now.... you can max it... as you can see if any captcha occurs then program open the new window so prblem will be easily takles and program will go on....
        try:
            print(f"Scraping URLs from: {url}")
            scraped_urls = scrape_urls(driver, url, max_pages=8)

            # Create DataFrame with scraped URLs
            df = pd.DataFrame({'URL': scraped_urls})

            # Concatenate with existing DataFrame
            final_df = pd.concat([final_df, df], ignore_index=True)

            # Update the CSV file after each iteration
            final_df.to_csv(final_csv, index=False)

        finally:
            # Close the driver after scraping URLs from current page
            driver.quit()

    print(f"All URLs scraped and saved in {final_csv}")

if __name__ == "__main__":
    main()
