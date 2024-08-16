import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException
import pickle

def load_cookies(driver, path):
    with open(path, 'rb') as file:
        cookies = pickle.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)

def scrape_urls(base_url, max_pages):
    service = Service(ChromeDriverManager().install())
    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(base_url)
        load_cookies(driver, "cookies.pkl")
        driver.refresh()
        time.sleep(5)  # wait for cookies to take effect

        all_urls = []
        current_page = 0

        while current_page < max_pages:
            current_page += 1

            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            div_tags = soup.find_all('div', class_='col-6 col-md-3')
            urls = [f"https://www.truepeoplesearch.com{div.find('a')['href']}/1" for div in div_tags]
            all_urls.extend(urls)

            # Check if there is a next page link
            next_page_link = soup.find('a', text=str(current_page + 1))
            if not next_page_link:
                print("No more pages found. Exiting...")
                break

            # Construct URL for the next page
            next_page_url = f"{base_url}?page={current_page + 1}"

            # Navigate to the next page
            driver.get(next_page_url)

    except WebDriverException as e:
        print(f"WebDriverException occurred: {e}")
    except Exception as e:
        print(f"Other Exception occurred: {e}")

    finally:
        driver.quit()
        service.stop()

    return all_urls

def main():
    base_url = "https://www.truepeoplesearch.com/find/b"   # change the URL category here
    max_pages = 7  # Limit the number of pages to scrape for demonstration

    all_urls = scrape_urls(base_url, max_pages)

    # Convert the list of URLs to a DataFrame
    df = pd.DataFrame(all_urls, columns=['URL'])

    # Save DataFrame to CSV
    output_file = "1.csv"
    df.to_csv(output_file, index=False)

    print(f"Scraped URLs saved in {output_file}")

if __name__ == "__main__":
    main()
