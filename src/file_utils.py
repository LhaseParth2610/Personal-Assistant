from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json
import time

def scrape_amazon_products(query, max_products=5):
    """Scrape top products from Amazon search results."""
    # Configure headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # Headless mode
    chrome_options.add_argument("--window-size=1920,1080")  # Standard window size
    chrome_options.add_argument("--disable-gpu")  # Disable GPU for headless
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
    )  # Set user-agent to avoid detection

    # Initialize WebDriver
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)  # Explicit wait for elements

    try:
        # Navigate to Amazon search page
        search_url = f"https://www.amazon.com/s?k={query.replace(' ', '+')}"
        driver.get(search_url)
        print(f"Navigating to: {search_url}")

        # Wait for product items to load
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".s-result-item.s-asin")))

        # Find product elements
        items = driver.find_elements(By.CSS_SELECTOR, ".s-result-item.s-asin")[:max_products * 2]  # Buffer for ads
        products = []

        for item in items:
            if len(products) >= max_products:
                break

            try:
                # Extract product name
                name_elem = item.find_elements(By.CSS_SELECTOR, "h2 a span")
                name = name_elem[0].text.strip() if name_elem else "N/A"

                # Extract price
                price_elem = item.find_elements(By.CSS_SELECTOR, ".a-price .a-offscreen")
                price = float(price_elem[0].get_attribute("innerText").replace("$", "").replace(",", "")) if price_elem else None

                # Extract rating
                rating_elem = item.find_elements(By.CSS_SELECTOR, ".a-icon-star-small .a-icon-alt")
                rating = float(rating_elem[0].get_attribute("innerText").split()[0]) if rating_elem else 0.0

                # Extract number of reviews
                reviews_elem = item.find_elements(By.CSS_SELECTOR, ".a-size-small .a-link-normal span")
                reviews = int(reviews_elem[0].text.replace(",", "")) if reviews_elem and reviews_elem[0].text.replace(",", "").isdigit() else 0

                # Extract product URL
                url_elem = item.find_elements(By.CSS_SELECTOR, "h2 a")
                url = url_elem[0].get_attribute("href") if url_elem else "N/A"

                # Extract image URL
                image_elem = item.find_elements(By.CSS_SELECTOR, ".s-image")
                image_url = image_elem[0].get_attribute("src") if image_elem else "N/A"

                # Skip sponsored products or incomplete data
                if "Sponsored" in item.text or not name or name == "N/A":
                    continue

                # Store product data
                product = {
                    "name": name,
                    "price": price,
                    "rating": rating,
                    "reviews": reviews,
                    "url": url,
                    "image_url": image_url
                }
                products.append(product)

            except (NoSuchElementException, ValueError) as e:
                print(f"Error processing item: {e}")
                continue

        return products

    except TimeoutException:
        print("Error: Timed out waiting for product items to load. Possible CAPTCHA or network issue.")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []
    finally:
        driver.quit()
        print("Browser closed.")

if __name__ == "__main__":
    # Example query
    product_query = "wireless earbuds"
    print(f"Scraping top 5 products for: {product_query}")

    # Scrape products
    results = scrape_amazon_products(product_query, max_products=5)

    # Print results in JSON format
    print("\nScraped Products:")
    print(json.dumps(results, indent=2))

    # Basic summary
    if results:
        print(f"\nFound {len(results)} products:")
        for i, product in enumerate(results, 1):
            print(f"{i}. {product['name']} - ${product['price']:.2f} (Rating: {product['rating']}/5, {product['reviews']} reviews)")
    else:
        print("\nNo products found. Try a different query or check Amazon's response.")