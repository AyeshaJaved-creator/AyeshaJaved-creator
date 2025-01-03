import httpx
from selectolax.parser import HTMLParser
import json
from rich import print
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

def load_stores():
    with open("stores.json", "r") as f:
        data = json.load(f)
    return [Store(**item) for item in data]

def load_page(client, url):
    try:
        resp = client.get(url, timeout=30.0)  # Increase timeout to 30 seconds
        return HTMLParser(resp.text)
    except httpx.ReadTimeout:
        print(f"Request to {url} timed out.")
        return None

def parse(store, html):
    title_element = html.css_first(store.title) if html else None
    price_element = html.css_first(store.price) if html else None

    if title_element:
        print(f"Found Title for {store.name}: {title_element.text(strip=True)}")
    else:
        print(f"Title not found for {store.name}. Raw HTML snippet: {html.text()[:500]}")

    if price_element:
        print(f"Found Price for {store.name}: {price_element.text(strip=True)}")
    else:
        print(f"Price not found for {store.name}. Raw HTML snippet: {html.text()[:500]}")

    title = title_element.text(strip=True) if title_element else "Title not found"
    price = price_element.text(strip=True) if price_element else "Price not found"

    return Item(store=store, title=title, price=price)

def store_selector(stores, url):
    for store in stores:
        if store.url in url:
            return store
    return None

def main():
    stores = load_stores()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    }
    client = httpx.Client(headers=headers)

    urls = [
        "https://rab.equipment/uk/womens-khroma-converge-gore-tex-jacket?queryID=d5d922264afc1239fde27abfad462b09&objectID=68805&indexName=rab_live_uk_products&_gl=1*1bct61x*_up*MQ..*_ga*MTkwNTI1OTUxMy4xNzM1ODMxMDYw*_ga_GH01DCFF89*MTczNTgzMTA1Ny4xLjAuMTczNTgzMTA1Ny4wLjAuODg2NDQ0NDky",
        "https://www.fjallraven.com/uk/en-gb/women/jackets/parkas/nuuk-parka-w2/?_t_q=&_t_hit.id=Luminos_Storefront_Web_Features_Catalog_Product_Domain_CommonProduct/CatalogContent_e79684c1-a080-44dc-b42b-981362d2dbeb_en-GB&_t_hit.pos=1&_t_tags=language%3aen%2candquerymatch%2csiteid%3a162d49d9-f0ac-4d2d-a110-e8143f6ca828&v=F86369::7323450789596",
        "https://www.blackdiamondequipment.com/en_US/product/womens-access-down-hoody/?colorid=23425"
        "https://www.amazon.co.uk/Magnifying-Illuminated-Cosmetic-Standing-Portable/dp/B06Y2MZH39?ref_=Oct_d_omg_d_10745681_5&pd_rd_w=c3kqA&content-id=amzn1.sym.ec8f623a-d4f7-4017-b387-58abf6ea18ca&pf_rd_p=ec8f623a-d4f7-4017-b387-58abf6ea18ca&pf_rd_r=M891588420BJRM6CDQJS&pd_rd_wg=x52Dr&pd_rd_r=9f674943-60cc-47b4-9bb1-12855621a074&pd_rd_i=B06Y2MZH39"
    ]

    for url in urls:
        store = store_selector(stores, url)
        if store:  # Check if store is found
            html = load_page(client, url)
            if html:  # Check if page was successfully loaded
                item = parse(store, html)
                print(item)
            else:
                print(f"Failed to load page for {url}")
        else:
            print(f"Store not found for URL: {url}")

if __name__ == "__main__": 
    main()

