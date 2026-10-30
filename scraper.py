from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup, Tag
import pandas as pd
import time
import re

def setup_browser():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver

def search_product(driver, phone_name):
    print(f"\n🔍 Searching Flipkart for: {phone_name}")
    search_url = f"https://www.flipkart.com/search?q={phone_name.replace(' ', '+')}&category=tyy%2C4io"
    driver.get(search_url)
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Find first product link
    links = soup.find_all("a", href=True)
    for link in links:
        # Ensure the element is a Tag and has get method (static analyzers may warn otherwise)
        if not isinstance(link, Tag):
            continue
        href = link.get("href")
        if not isinstance(href, str):
            continue
        if "/p/" in href and "pid=" in href:
            full_url = "https://www.flipkart.com" + href
            # Convert product URL to review URL
            review_url = full_url.replace("/p/", "/product-reviews/")
            # Clean extra params and add review params
            base = review_url.split("?")[0]
            pid = re.search(r"pid=([^&]+)", full_url)
            if pid:
                final_url = f"{base}?pid={pid.group(1)}&sortOrder=MOST_HELPFUL&certifiedBuyer=false&aid=overall"
                print(f"✅ Found product URL!")
                return final_url

    print("❌ Product not found. Try a different name.")
    return None

def scrape_reviews(driver, product_name, base_url, pages=10):
    all_reviews = []
    print(f"\n📥 Scraping reviews for: {product_name}")

    for page in range(1, pages + 1):
        url = base_url + f"&page={page}"
        driver.get(url)
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        for div in soup.find_all("div"):
            text = div.get_text(strip=True)
            if re.match(r"^\d\.\d•", text) and "Verified Purchase" in text and len(text) < 600:
                rating_match = re.match(r"^(\d\.\d)", text)
                if not rating_match:
                    continue
                rating = rating_match.group(1)

                title_match = re.search(r"•(.+?)Review for", text)
                title = title_match.group(1).strip() if title_match else "N/A"

                body_match = re.search(r"\d+ GB(.+?)(?:Helpful for|$)", text)
                body = body_match.group(1).strip() if body_match else "N/A"

                if len(body) > 5:
                    all_reviews.append({
                        "product": product_name,
                        "rating": float(rating),
                        "title": title,
                        "review": body
                    })

        print(f"  Page {page} — reviews so far: {len(all_reviews)}")

    return all_reviews

def clean_and_save(reviews, product_name):
    df = pd.DataFrame(reviews)
    df = df.drop_duplicates(subset=["review"])

    df["review"] = df["review"].apply(
        lambda x: re.sub(r"^•\s*Storage\s*\d+\s*GB", "", str(x)).strip()
    )
    df["review"] = df["review"].apply(
        lambda x: re.sub(r"[A-Z][a-z]+\s+[A-Z][a-z]+,\s*\w+$", "", str(x)).strip()
    )
    df = df[df["review"].str.len() > 10]
    df = df.reset_index(drop=True)

    filename = product_name.replace(" ", "_").lower() + "_reviews.csv"
    df.to_csv(filename, index=False)

    print(f"\n✅ Saved {len(df)} clean reviews to '{filename}'")
    print(df[["rating", "title", "review"]].head(5).to_string())
    return filename

# ── Main Program ──
driver = setup_browser()
print("✅ Browser ready!")

while True:
    print("\n" + "="*40)
    print("   📱 MOBILE SENTIMENT ANALYZER")
    print("="*40)
    phone = input("Enter phone name (or 'exit' to quit): ").strip()

    if phone.lower() == "exit":
        print("\nGoodbye! 👋")
        break

    # Step 1 — Search and find URL automatically
    review_url = search_product(driver, phone)

    if review_url:
        # Step 2 — Scrape reviews
        reviews = scrape_reviews(driver, phone, review_url)

        if reviews:
            # Step 3 — Clean and save
            clean_and_save(reviews, phone)
        else:
            print("❌ No reviews found for this product.")

driver.quit()