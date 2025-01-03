import os
import time
import random
import csv
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from tabulate import tabulate

# User-agent list to mimic different browsers
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
]

def initialize_driver(proxy_ip, proxy_port):
  """Initialize Selenium WebDriver with proxy."""
  options = webdriver.ChromeOptions()
  options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
  options.add_argument("--headless")  # Optional: Enable headless mode

  # Set proxy configuration
  proxy = Proxy(
      proxy_type=ProxyType.HTTP,
      http_proxy=f"{proxy_ip}:{proxy_port}"
  )
  options.add_argument(proxy.add_to_launcher())

  driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
  return driver

def scrape_amazon_category(url, max_pages=2, proxy_ip=None, proxy_port=None):
  """Scrape product details from an Amazon category using Selenium with proxy."""
  driver = None
  try:
    driver = initialize_driver(proxy_ip, proxy_port)
    products = []
    for page in range(1, max_pages + 1):
      print(f"\nScraping page {page}...")
      try:
        driver.get(f"{url}&page={page}")
        WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".s-main-slot .s-result-item"))
        )
        product_cards = driver.find_elements(By.CSS_SELECTOR, ".s-main-slot .s-result-item")
        print(f"Found {len(product_cards)} products on page {page}.")

        for card in product_cards:
          product_data = {}
          # Title
          try:
            product_data['Title'] = card.find_element(By.CSS_SELECTOR, "h2.a-size-base-plus span").text.strip()
          except Exception:
            product_data['Title'] = 'N/A'
          # Price
          try:
            product_data['Price'] = card.find_element(By.CSS_SELECTOR, "span.a-price-whole").text.strip()
          except Exception:
            product_data['Price'] = 'N/A'
          # Buyers Count (Assuming this element exists on the website)
          try:
            product_data['Buyers'] = card.find_element(By.CSS_SELECTOR, "span.s-underline-text").text.strip()
          except Exception:
            product_data['Buyers'] = 'N/A'
          # Image URL
          try:
            product_data['Image URL'] = card.find_element(By.CSS_SELECTOR, "img.s-image").get_attribute("src")
          except Exception:
            product_data['Image URL'] = 'N/A'

          products.append(product_data)
          time.sleep(random.uniform(3, 10))  # Mimic human browsing
      except TimeoutException:
        print(f"Timeout waiting for page to load.")
      except Exception as e:
        print(f"Error on page {page}: {e}")
        continue

    return products
  except Exception as e:
    print(f"An error occurred during scraping: {e}")
    return []
  finally:
    if driver:
      try:
        driver.quit()
      except Exception as e:
        print(f"Error quitting driver: {e}")

def save_to_csv(data, filename="amazon_products.csv"):
  """Save scraped data to a CSV file."""
  if not data:
    print("No data to save.")
    return
  with open(filename, mode="w", newline="", encoding="utf-8") as file:
    fieldnames = ["Title", "Price", "Buyers", "Image URL"]
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)
  print(f"Saved {len(data)} products to {filename}")

def main():
  """Main function to scrape Amazon and save results."""
  url = "https://www.amazon.com/s?i=specialty-aps&bbn=4954955011&rh=n%3A4954955011%2Cn%3A%25212617942011%2Cn%3A12897221&ref=nav_em__nav_desktop_sa_intl_knitning_crochet_0_2_8_7"

  # Replace with your actual proxy IP and port
  proxy_ip = "your_proxy_ip" 
  proxy_port = "your_proxy_port" 

  try:
    products = scrape_amazon_category(url, max_pages=2, proxy_ip=proxy_ip, proxy_port=proxy_port)

    if products:
      print("\nScraped Products:")
      print(tabulate(products[:5], headers="keys", tablefmt="grid"))
      save_to_csv(products)
    else:
      print("No products scraped.")
  except Exception as e:
    print(f"Error: {e}")

if __name__ == "__main__":
  main()