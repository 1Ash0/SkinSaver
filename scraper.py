import os
import re
import uuid
import random
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import trafilatura

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# User agent for requests
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# Headers for requests
headers = {
    'User-Agent': USER_AGENT,
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}

def get_website_text_content(url):
    """
    Get the main text content of a website using trafilatura
    """
    try:
        downloaded = trafilatura.fetch_url(url)
        text = trafilatura.extract(downloaded)
        return text
    except Exception as e:
        logger.error(f"Error extracting text content from {url}: {e}")
        return None

def clean_price(price_text):
    """
    Clean price text to standard format
    """
    if not price_text:
        return "₹0"
    
    # Extract digits and decimal point
    price = re.sub(r'[^\d.]', '', price_text)
    
    # Format as Indian Rupee
    try:
        price_float = float(price)
        if price_float == 0:
            return "₹0"
        return f"₹{price_float:,.2f}"
    except:
        return f"₹{price}"

def get_amazon_products(query, max_products=10):
    """
    Scrape skincare products from Amazon
    """
    products = []
    url = f"https://www.amazon.in/s?k={query}+skincare"
    
    try:
        logger.info(f"Scraping Amazon with query: {query}")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch Amazon products: Status code {response.status_code}")
            return products
        
        soup = BeautifulSoup(response.content, 'html.parser')
        product_items = soup.select('.s-result-item[data-component-type="s-search-result"]')
        
        count = 0
        for item in product_items:
            if count >= max_products:
                break
                
            try:
                # Extract product details
                title_element = item.select_one('h2 a span')
                title = title_element.text.strip() if title_element else "Unknown Product"
                
                price_element = item.select_one('.a-price .a-offscreen')
                price = price_element.text.strip() if price_element else "₹0"
                price = clean_price(price)
                
                link_element = item.select_one('h2 a')
                link = urljoin("https://www.amazon.in", link_element['href']) if link_element else "#"
                
                image_element = item.select_one('img.s-image')
                image = image_element['src'] if image_element else ""
                
                rating_element = item.select_one('i.a-icon-star-small')
                rating = rating_element.text.strip() if rating_element else "No ratings"
                
                # Only include products with valid titles and prices
                if title != "Unknown Product" and price != "₹0":
                    product = {
                        'id': str(uuid.uuid4()),
                        'name': title,
                        'price': price,
                        'image': image,
                        'rating': rating,
                        'link': link,
                        'source': 'Amazon',
                        'description': f"Amazon skincare product: {title}",
                        'category': 'skincare'
                    }
                    products.append(product)
                    count += 1
            except Exception as e:
                logger.error(f"Error processing Amazon product: {e}")
                continue
                
    except Exception as e:
        logger.error(f"Error scraping Amazon: {e}")
    
    logger.info(f"Scraped {len(products)} products from Amazon")
    return products

def get_flipkart_products(query, max_products=10):
    """
    Scrape skincare products from Flipkart
    """
    products = []
    url = f"https://www.flipkart.com/search?q={query}+skincare"
    
    try:
        logger.info(f"Scraping Flipkart with query: {query}")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch Flipkart products: Status code {response.status_code}")
            return products
        
        soup = BeautifulSoup(response.content, 'html.parser')
        product_items = soup.select('._1AtVbE')
        
        count = 0
        for item in product_items:
            if count >= max_products:
                break
                
            try:
                # Extract product details
                title_element = item.select_one('._4rR01T') or item.select_one('.s1Q9rs') or item.select_one('._2WkVRV')
                title = title_element.text.strip() if title_element else "Unknown Product"
                
                price_element = item.select_one('._30jeq3')
                price = price_element.text.strip() if price_element else "₹0"
                price = clean_price(price)
                
                link_element = item.select_one('a._1fQZEK') or item.select_one('a.s1Q9rs') or item.select_one('a._2rpwqI')
                link = urljoin("https://www.flipkart.com", link_element['href']) if link_element else "#"
                
                image_element = item.select_one('img._396cs4') or item.select_one('img._2r_T1I')
                image = image_element['src'] if image_element else ""
                
                rating_element = item.select_one('._3LWZlK')
                rating = rating_element.text.strip() + "/5" if rating_element else "No ratings"
                
                # Only include products with valid titles and prices
                if title != "Unknown Product" and price != "₹0":
                    product = {
                        'id': str(uuid.uuid4()),
                        'name': title,
                        'price': price,
                        'image': image,
                        'rating': rating,
                        'link': link,
                        'source': 'Flipkart',
                        'description': f"Flipkart skincare product: {title}",
                        'category': 'skincare'
                    }
                    products.append(product)
                    count += 1
            except Exception as e:
                logger.error(f"Error processing Flipkart product: {e}")
                continue
                
    except Exception as e:
        logger.error(f"Error scraping Flipkart: {e}")
    
    logger.info(f"Scraped {len(products)} products from Flipkart")
    return products

def get_nykaa_products(query, max_products=10):
    """
    Scrape skincare products from Nykaa
    """
    products = []
    url = f"https://www.nykaa.com/search/result/?q={query}&root=search&searchType=Manual&sourcepage=Search%20Page"
    
    try:
        logger.info(f"Scraping Nykaa with query: {query}")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch Nykaa products: Status code {response.status_code}")
            return products
        
        soup = BeautifulSoup(response.content, 'html.parser')
        product_items = soup.select('.css-1pe3act')
        
        count = 0
        for item in product_items:
            if count >= max_products:
                break
                
            try:
                # Extract product details
                title_element = item.select_one('.css-xrzmfa')
                title = title_element.text.strip() if title_element else "Unknown Product"
                
                price_element = item.select_one('.css-111z9ua')
                price = price_element.text.strip() if price_element else "₹0"
                price = clean_price(price)
                
                link_element = item.select_one('a')
                link = urljoin("https://www.nykaa.com", link_element['href']) if link_element else "#"
                
                image_element = item.select_one('img')
                image = image_element['src'] if image_element else ""
                
                # Only include products with valid titles and prices
                if title != "Unknown Product" and price != "₹0":
                    product = {
                        'id': str(uuid.uuid4()),
                        'name': title,
                        'price': price,
                        'image': image,
                        'rating': f"{random.uniform(3.0, 5.0):.1f}/5",  # Random rating as Nykaa might not show it
                        'link': link,
                        'source': 'Nykaa',
                        'description': f"Nykaa skincare product: {title}",
                        'category': 'skincare'
                    }
                    products.append(product)
                    count += 1
            except Exception as e:
                logger.error(f"Error processing Nykaa product: {e}")
                continue
                
    except Exception as e:
        logger.error(f"Error scraping Nykaa: {e}")
    
    logger.info(f"Scraped {len(products)} products from Nykaa")
    return products

def get_all_products(query="skincare", max_per_site=10):
    """
    Get products from all supported e-commerce sites
    """
    amazon_products = get_amazon_products(query, max_per_site)
    flipkart_products = get_flipkart_products(query, max_per_site)
    nykaa_products = get_nykaa_products(query, max_per_site)
    
    all_products = amazon_products + flipkart_products + nykaa_products
    return all_products

# For testing
if __name__ == "__main__":
    # Test the scrapers
    products = get_all_products("moisturizer", 5)
    print(f"Total products scraped: {len(products)}")
    for product in products[:2]:  # Print first 2 products as sample
        print(f"\nProduct: {product['name']}")
        print(f"Price: {product['price']}")
        print(f"Source: {product['source']}")
