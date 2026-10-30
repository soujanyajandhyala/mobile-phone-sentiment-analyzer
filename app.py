import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup, Tag
import time
import re

nltk.download('vader_lexicon', quiet=True)

st.set_page_config(
    page_title="Mobile Sentiment Analyzer",
    page_icon="📱",
    layout="wide"
)

# ── Sidebar ──
st.sidebar.title("⚙️ Display Options")
st.sidebar.markdown("Choose what to show after analysis:")
show_pie = st.sidebar.checkbox("📊 Sentiment Pie Chart", value=True)
show_bar = st.sidebar.checkbox("📈 Rating Distribution", value=True)
show_wordcloud = st.sidebar.checkbox("☁️ Word Clouds", value=True)
show_top_reviews = st.sidebar.checkbox("💬 Top Reviews", value=True)
show_table = st.sidebar.checkbox("📄 Raw Data Table", value=False)

st.sidebar.markdown("---")
st.sidebar.markdown("**About**")
st.sidebar.info("This app scrapes real Flipkart reviews and analyzes customer sentiment using VADER NLP.")

# ── Main ──
st.title("📱 Mobile Phone Sentiment Analyzer")
st.markdown("Select any phone → scrape real reviews → see overall customer emotion")

@st.cache_resource
def get_driver():
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
    search_url = f"https://www.flipkart.com/search?q={phone_name.replace(' ', '+')}&category=tyy%2C4io"
    driver.get(search_url)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    links = soup.find_all("a", href=True)
    for link in links:
        href = link.attrs.get("href", "") if isinstance(link, Tag) else ""
        if href and "/p/" in href and "pid=" in href:
            full_url = "https://www.flipkart.com" + str(href)
            review_url = full_url.replace("/p/", "/product-reviews/")
            base = review_url.split("?")[0]
            pid = re.search(r"pid=([^&]+)", full_url)
            if pid:
                return f"{base}?pid={pid.group(1)}&sortOrder=MOST_HELPFUL&certifiedBuyer=false&aid=overall"
    return None

def scrape_reviews(driver, base_url, pages=5):
    all_reviews = []
    for page in range(1, pages + 1):
        url = base_url + f"&page={page}"
        driver.get(url)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        for div in soup.find_all("div"):
            text = div.get_text(strip=True)
            if re.match(r"^\d\.\d•", text) and "Verified Purchase" in text and len(text) < 600:
                rating_match = re.match(r"^(\d\.\d)", text)
                rating = rating_match.group(1) if rating_match else "0.0"
                title_match = re.search(r"•(.+?)Review for", text)
                title = title_match.group(1).strip() if title_match else "N/A"
                body_match = re.search(r"\d+ GB(.+?)(?:Helpful for|$)", text)
                body = body_match.group(1).strip() if body_match else "N/A"
                if len(body) > 5:
                    all_reviews.append({
                        "rating": float(rating),
                        "title": title,
                        "review": body
                    })
    df = pd.DataFrame(all_reviews).drop_duplicates(subset=["review"])
    df["review"] = df["review"].apply(
        lambda x: re.sub(r"^•\s*Storage\s*\d+\s*GB", "", str(x)).strip()
    )
    return df.reset_index(drop=True)

def analyze(df):
    sia = SentimentIntensityAnalyzer()
    results = []
    for _, row in df.iterrows():
        score = sia.polarity_scores(str(row['review']))['compound']
        sentiment = "Positive" if score >= 0.05 else "Negative" if score <= -0.05 else "Neutral"
        results.append({**row, "compound_score": score, "sentiment": sentiment})
    return pd.DataFrame(results)

# ── Phone selector ──
col1, col2 = st.columns([3, 1])
with col1:
    phone_name = st.selectbox("📱 Select a phone", [
        "Samsung Galaxy S25",
        "Samsung Galaxy S25 FE",
        "Samsung Galaxy S25 Ultra",
        "iPhone 16",
        "iPhone 16 Pro",
        "iPhone 16 Pro Max",
        "OnePlus 13",
        "OnePlus Nord 4",
        "Google Pixel 9",
        "Google Pixel 9 Pro",
        "Xiaomi 14",
        "Xiaomi 14 Ultra",
        "Nothing Phone 2a",
        "Redmi Note 13 Pro",
        "POCO X6 Pro",
        "Vivo V30 Pro",
        "OPPO Reno 12 Pro",
        "Motorola Edge 50 Ultra"
    ])
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    analyze_btn = st.button("Analyze Sentiment 🚀", use_container_width=True)

if analyze_btn and phone_name:
    driver = get_driver()

    with st.spinner(f"Searching Flipkart for {phone_name}..."):
        url = search_product(driver, phone_name)

    if not url:
        st.error("Product not found!")
    else:
        with st.spinner("Scraping reviews..."):
            df = scrape_reviews(driver, url, 5)

        if df.empty:
            st.error("No reviews found!")
        else:
            with st.spinner("Analyzing sentiment..."):
                result_df = analyze(df)

            total = len(result_df)
            pos = len(result_df[result_df['sentiment'] == 'Positive'])
            neu = len(result_df[result_df['sentiment'] == 'Neutral'])
            neg = len(result_df[result_df['sentiment'] == 'Negative'])
            avg_score = result_df['compound_score'].mean()
            normalized = round((avg_score + 1) * 50)
            avg_rating = result_df['rating'].mean()

            if (pos/total)*100 >= 70:
                emotion = "😍 Delighted"
            elif (pos/total)*100 >= 50:
                emotion = "😊 Satisfied"
            elif (neg/total)*100 >= 50:
                emotion = "😞 Disappointed"
            elif (neg/total)*100 >= 30:
                emotion = "😤 Frustrated"
            else:
                emotion = "😐 Divided"

            st.success(f"✅ Analyzed {total} reviews for **{phone_name}**")
            st.markdown("---")
            st.markdown(f"## Overall Emotion: {emotion}")

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Sentiment Score", f"{normalized}/100")
            col2.metric("Positive Reviews", f"{round((pos/total)*100)}%")
            col3.metric("Average Rating", f"{round(avg_rating,1)} ⭐")
            col4.metric("Total Reviews", total)

            st.markdown("---")

            # ── Pie Chart ──
            if show_pie:
                st.subheader("📊 Sentiment Pie Chart")
                fig, ax = plt.subplots()
                ax.pie([pos, neu, neg],
                       labels=['Positive', 'Neutral', 'Negative'],
                       colors=['#639922', '#888780', '#E24B4A'],
                       autopct='%1.1f%%', startangle=90)
                st.pyplot(fig)
                plt.close()
                st.markdown("---")

            # ── Bar Chart ──
            if show_bar:
                st.subheader("📈 Rating Distribution")
                fig, ax = plt.subplots()
                rating_counts = result_df['rating'].value_counts().sort_index()
                # convert to numpy arrays to avoid ExtensionArray type issues with matplotlib
                x_vals = rating_counts.index.to_numpy()
                y_vals = rating_counts.to_numpy()
                ax.bar(x_vals, y_vals,
                       color=['#E24B4A','#E24B4A','#888780','#639922','#639922'][:len(y_vals)])
                ax.set_xlabel("Rating")
                ax.set_ylabel("Number of Reviews")
                st.pyplot(fig)
                plt.close()
                st.markdown("---")

            # ── Word Clouds ──
            if show_wordcloud:
                st.subheader("☁️ Word Clouds")
                pos_text = " ".join(result_df[result_df['sentiment']=='Positive']['review'].tolist())
                neg_text = " ".join(result_df[result_df['sentiment']=='Negative']['review'].tolist())
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Positive Reviews**")
                    if pos_text.strip():
                        wc = WordCloud(width=600, height=300, background_color='white', colormap='Greens').generate(pos_text)
                        fig, ax = plt.subplots()
                        ax.imshow(wc)
                        ax.axis('off')
                        st.pyplot(fig)
                        plt.close()
                with col2:
                    st.markdown("**Negative Reviews**")
                    if neg_text.strip():
                        wc = WordCloud(width=600, height=300, background_color='white', colormap='Reds').generate(neg_text)
                        fig, ax = plt.subplots()
                        ax.imshow(wc)
                        ax.axis('off')
                        st.pyplot(fig)
                        plt.close()
                    else:
                        st.info("Not enough negative reviews!")
                st.markdown("---")

            # ── Top Reviews ──
            if show_top_reviews:
                st.subheader("💬 Top Reviews")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**✅ Most Positive**")
                    top_pos = result_df[result_df['sentiment']=='Positive'].nlargest(3,'compound_score')
                    for _, r in top_pos.iterrows():
                        st.success(f"⭐ {r['rating']} — {r['review'][:150]}")
                with col2:
                    st.markdown("**❌ Most Negative**")
                    top_neg = result_df[result_df['sentiment']=='Negative'].nsmallest(3,'compound_score')
                    if len(top_neg) > 0:
                        for _, r in top_neg.iterrows():
                            st.error(f"⭐ {r['rating']} — {r['review'][:150]}")
                    else:
                        st.info("No negative reviews found!")
                st.markdown("---")

            # ── Raw Data ──
            if show_table:
                st.subheader("📄 All Reviews Data")
                st.dataframe(result_df[['rating','title','review','sentiment','compound_score']])