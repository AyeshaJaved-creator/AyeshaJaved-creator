import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selectolax.parser import HTMLParser
import json
from dataclasses import dataclass

@dataclass
class Store:
    name: str
    url: str
    title: str
    price: str

@dataclass
class Item:
    store: Store
    title: str
    price: str

def load_stores(filename="stores.json"):
    """Load store data from a JSON file."""
    try:
        with open(filename, "r") as f:
            data = json.load(f)
        return [Store(**item) for item in data]
    except Exception as e:
        print(f"[Error] Failed to load stores: {e}")
        return []

def create_driver():
    """Create a Selenium driver using undetected_chromedriver."""
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-blink-features=AutomationControlled")
        driver = uc.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        return driver
    except Exception as e:
        print(f"[Error] Failed to create driver: {e}")
        return None

def load_page_with_selenium(driver, url):
    """Load the page using Selenium and return the HTML."""
    try:
        driver.get(url)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        return HTMLParser(driver.page_source)
    except Exception as e:
        print(f"[Error] Failed to load page {url}: {e}")
        return None

def parse(store, html):
    """Parse the product title and price from the HTML."""
    try:
        # Extracting title
        title_element = html.css_first(store.title)
        title = title_element.text(strip=True) if title_element else "Title not found"

        # Extracting price
        price = "Price not found"
        if store.name == "Amazon":
            # Amazon-specific price extraction
            price_whole = html.css_first("span.a-price-whole")
            price_decimal = html.css_first("span.a-price-decimal")
            if price_whole:
                price = price_whole.text(strip=True)
                if price_decimal:
                    price += "." + price_decimal.text(strip=True)
        else:
            price_element = html.css_first(store.price)
            price = price_element.text(strip=True) if price_element else "Price not found"

        return Item(store=store, title=title, price=price)
    except Exception as e:
        print(f"[Error] Failed to parse data for {store.name}: {e}")
        return Item(store=store, title="Title not found", price="Price not found")

def store_selector(stores, url):
    """Select the appropriate store configuration for a given URL."""
    for store in stores:
        if store.url in url:
            return store
    return None

def main():
    """Main entry point for the scraper."""
    stores = load_stores("stores.json")
    if not stores:
        print("[Error] No stores loaded. Exiting.")
        return

    driver = create_driver()
    if not driver:
        print("[Error] Failed to initialize web driver. Exiting.")
        return

    urls = [
        "https://rab.equipment/uk/womens-khroma-converge-gore-tex-jacket?queryID=d5d922264afc1239fde27abfad462b09&objectID=68805&indexName=rab_live_uk_products&_gl=1*1bct61x*_up*MQ..*_ga*MTkwNTI1OTUxMy4xNzM1ODMxMDYw*_ga_GH01DCFF89*MTczNTgzMTA1Ny4xLjAuMTczNTgzMTA1Ny4wLjAuODg2NDQ0NDky",
        "https://www.fjallraven.com/uk/en-gb/women/jackets/parkas/nuuk-parka-w2/?_t_q=&_t_hit.id=Luminos_Storefront_Web_Features_Catalog_Product_Domain_CommonProduct/CatalogContent_e79684c1-a080-44dc-b42b-981362d2dbeb_en-GB&_t_hit.pos=1&_t_tags=language%3aen%2candquerymatch%2csiteid%3a162d49d9-f0ac-4d2d-a110-e8143f6ca828&v=F86369::7323450789596",
        "https://www.blackdiamondequipment.com/en_US/product/womens-access-down-hoody/?colorid=23425",
        "https://www.amazon.co.uk/dp/B09THCJJYK/ref=sspa_dk_detail_0?pd_rd_i=B09THCJJYK&pd_rd_w=ejZ73&content-id=amzn1.sym.7b0d8b34-54be-4fd2-9baf-2d658b11dc53&pf_rd_p=7b0d8b34-54be-4fd2-9baf-2d658b11dc53&pf_rd_r=RGJZPQGZA7BN4ABD80DY&pd_rd_wg=UzdZ1&pd_rd_r=647efe73-92b7-4396-af0d-9afb1dc5eeb6&s=kitchen&sp_csd=d2lkZ2V0TmFtZT1zcF9kZXRhaWxfdGhlbWF0aWM&th=1"
    ]

    for url in urls:
        store = store_selector(stores, url)
        if store:
            html = load_page_with_selenium(driver, url)
            if html:
                item = parse(store, html)
                print(item)
            else:
                print(f"[Error] Failed to load page for URL: {url}")
        else:
            print(f"[Error] Store not found for URL: {url}")

    driver.quit()

if __name__ == "__main__":
    main()
