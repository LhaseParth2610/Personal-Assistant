import os
import re
import threading
import json
from mistralai import Mistral
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc
import time

# Load environment variables
load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")

class EcommerceAssistant:
    def __init__(self, display_callback, input_callback):
        self.display_callback = display_callback
        self.input_callback = input_callback
        self.driver = None
        self.wait = None
        self.selenium_initialized = False
        self.feedback_active = False

    def setup_selenium(self):
        """Set up Selenium with Brave browser."""
        if self.selenium_initialized:
            return

        BRAVE_BINARY = "/usr/bin/brave"  # Update for your system
        chrome_driver_path = os.path.abspath("chromedriver")
        PROFILE_DIR = os.path.expanduser("~/.config/BraveSoftware/Brave-Browser-Automation")  # Dedicated profile

        options = uc.ChromeOptions()
        options.binary_location = BRAVE_BINARY
        options.add_argument(f"--user-data-dir={PROFILE_DIR}")
        options.add_argument("--headless=new")
        options.add_argument("--profile-directory=Default")
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124")

        self.driver = uc.Chrome(options=options, driver_executable_path=chrome_driver_path)
        self.wait = WebDriverWait(self.driver, 10)
        self.selenium_initialized = True

    def cleanup(self):
        """Clean up Selenium driver."""
        if self.driver and self.selenium_initialized:
            self.driver.quit()
            self.selenium_initialized = False

    def parse_query(self, prompt):
        """Parse e-commerce query using Mistral LLM."""
        with Mistral(api_key=api_key) as client:
            mistral_prompt = f"""
            Parse the following e-commerce query into product, budget, and preferences (e.g., style, pattern).
            Return JSON: {{ "product": str, "budget": float or null, "preferences": str or null }}
            Query: {prompt}
            """
            resp = client.chat.complete(
                model="open-mistral-7b",
                messages=[{"role": "user", "content": mistral_prompt}]
            )
            try:
                return json.loads(resp.choices[0].message.content)
            except:
                product = re.search(r'\b(buy|shop|find|get)\s+([a-z\s]+)', prompt, re.IGNORECASE)
                budget = re.search(r'\b(under|below)\s*\$?(\d+)', prompt, re.IGNORECASE)
                return {
                    "product": product.group(2).strip() if product else "unknown",
                    "budget": float(budget.group(2)) if budget else None,
                    "preferences": None
                }

    def fetch_amazon_results(self, product, sort_by=None):
        """Fetch product results from Amazon using Selenium."""
        self.setup_selenium()
        try:
            search_url = f"https://www.amazon.com/s?k={product.replace(' ', '+')}"
            if sort_by == "price":
                search_url += "&s=price-asc-rank"
            elif sort_by == "rating":
                search_url += "&s=review-rank"
            self.driver.get(search_url)
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".s-result-item")))

            results = []
            items = self.driver.find_elements(By.CSS_SELECTOR, ".s-result-item.s-asin")[:15]
            for item in items:
                try:
                    name = item.find_element(By.CSS_SELECTOR, "h2 a span").text
                    price_elem = item.find_elements(By.CSS_SELECTOR, ".a-price .a-offscreen")
                    price = float(price_elem[0].get_attribute("innerText").replace("$", "")) if price_elem else None
                    rating_elem = item.find_elements(By.CSS_SELECTOR, ".a-icon-star-small .a-icon-alt")
                    rating = float(rating_elem[0].get_attribute("innerText").split()[0]) if rating_elem else 0
                    reviews_elem = item.find_elements(By.CSS_SELECTOR, ".a-size-small .a-link-normal span")
                    reviews = int(reviews_elem[0].text.replace(",", "")) if reviews_elem else 0
                    url = item.find_element(By.CSS_SELECTOR, "h2 a").get_attribute("href")
                    image_elem = item.find_elements(By.CSS_SELECTOR, ".s-image")
                    image_url = image_elem[0].get_attribute("src") if image_elem else ""
                    description = item.find_elements(By.CSS_SELECTOR, ".s-description")
                    description = description[0].text if description else ""

                    if price and name:
                        results.append({
                            "name": name,
                            "price": price,
                            "rating": rating,
                            "reviews": reviews,
                            "url": url,
                            "image_url": image_url,
                            "description": description
                        })
                except (NoSuchElementException, ValueError):
                    continue
            return results
        except TimeoutException:
            self.display_callback("Error: Timed out while fetching Amazon results.")
            return []
        finally:
            pass

    def rank_results(self, results, budget=None):
        """Rank results into cheapest, highest-rated, and balanced."""
        if not results:
            return {"cheapest": [], "highest_rated": [], "balanced": []}

        filtered = [r for r in results if r["rating"] >= 3.5 and r["reviews"] >= 50 and (budget is None or r["price"] <= budget)]
        cheapest = sorted(filtered, key=lambda x: x["price"])[:5]
        highest_rated = sorted(filtered, key=lambda x: (-x["rating"], -x["reviews"]))[:5]
        if filtered:
            max_price = max(r["price"] for r in filtered)
            balanced = sorted(
                [r for r in filtered if r["rating"] >= 4.0],
                key=lambda x: (x["rating"] / 5) * 0.6 + (1 - x["price"] / max_price) * 0.4,
                reverse=True
            )[:5]
        else:
            balanced = []

        return {
            "cheapest": cheapest,
            "highest_rated": highest_rated,
            "balanced": balanced
        }

    def process_product_query(self, prompt, results_callback):
        """Process an e-commerce query and display results."""
        self.feedback_active = True
        query_info = self.parse_query(prompt)
        product = query_info["product"]
        budget = query_info["budget"]

        amazon_results = self.fetch_amazon_results(product)
        ranked_results = self.rank_results(amazon_results, budget)
        combined_results = []
        seen_urls = set()
        for category in ["cheapest", "highest_rated", "balanced"]:
            for result in ranked_results[category]:
                if result["url"] not in seen_urls:
                    combined_results.append(result)
                    seen_urls.add(result["url"])
                    if len(combined_results) >= 5:
                        break
            if len(combined_results) >= 5:
                break

        myntra_results = []
        flipkart_results = []

        self.display_callback("Displaying e-commerce results...")
        results_callback(combined_results, myntra_results, flipkart_results)

        while True:
            feedback = self.input_callback().strip()
            if feedback.lower() in ["satisfied", "yes"]:
                break
            else:
                self.process_feedback_query(feedback, combined_results, myntra_results, flipkart_results, results_callback)
        self.feedback_active = False

    def process_feedback_query(self, feedback, amazon_results, myntra_results, flipkart_results, results_callback):
        """Process feedback for refined e-commerce queries."""
        with Mistral(api_key=api_key) as client:
            mistral_prompt = f"""
            Parse feedback for refined e-commerce query. Return JSON:
            {{ "site": str or null, "price_range": str or null, "preferences": str or null }}
            Feedback: {feedback}
            """
            resp = client.chat.complete(
                model="open-mistral-7b",
                messages=[{"role": "user", "content": mistral_prompt}]
            )
            try:
                feedback_info = json.loads(resp.choices[0].message.content)
            except:
                feedback_info = {"site": None, "price_range": None, "preferences": None}

        site = feedback_info["site"]
        price_range = feedback_info["price_range"]
        preferences = feedback_info["preferences"]

        if site and "amazon" in site.lower():
            results = amazon_results
        else:
            results = amazon_results  # Default to Amazon for now

        if price_range and "medium" in price_range.lower():
            prices = [r["price"] for r in results]
            if prices:
                min_price, max_price = sorted(prices)[int(0.25 * len(prices))], sorted(prices)[int(0.75 * len(prices))]
                results = [r for r in results if min_price <= r["price"] <= max_price]

        if preferences and "pattern" in preferences.lower():
            with Mistral(api_key=api_key) as client:
                mistral_prompt = f"""
                Filter products with descriptions indicating stylish or unique patterns.
                Products: {json.dumps([r["description"] for r in results])}
                Return indices of matching products.
                """
                resp = client.chat.complete(
                    model="open-mistral-7b",
                    messages=[{"role": "user", "content": mistral_prompt}]
                )
                try:
                    indices = json.loads(resp.choices[0].message.content)
                    results = [results[i] for i in indices]
                except:
                    pass

        ranked_results = self.rank_results(results)
        combined_results = []
        seen_urls = set()
        for category in ["cheapest", "highest_rated", "balanced"]:
            for result in ranked_results[category]:
                if result["url"] not in seen_urls:
                    combined_results.append(result)
                    seen_urls.add(result["url"])
                    if len(combined_results) >= 5:
                        break
            if len(combined_results) >= 5:
                break

        results_callback(combined_results, myntra_results, flipkart_results)