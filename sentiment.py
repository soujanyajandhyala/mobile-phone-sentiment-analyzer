import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import os

# Download VADER
nltk.download('vader_lexicon', quiet=True)

sia = SentimentIntensityAnalyzer()

def analyze_sentiment(product_name, df):
    print(f"\n🤖 Analyzing {len(df)} reviews for {product_name}...")

    results = []
    for _, row in df.iterrows():
        score = sia.polarity_scores(str(row['review']))
        compound = score['compound']

        if compound >= 0.05:
            sentiment = "Positive"
        elif compound <= -0.05:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"

        results.append({
            "review": row['review'],
            "rating": row['rating'],
            "title": row['title'],
            "compound_score": compound,
            "sentiment": sentiment
        })

    result_df = pd.DataFrame(results)

    # Calculate overall stats
    total = len(result_df)
    pos = len(result_df[result_df['sentiment'] == 'Positive'])
    neg = len(result_df[result_df['sentiment'] == 'Negative'])
    neu = len(result_df[result_df['sentiment'] == 'Neutral'])
    avg_score = result_df['compound_score'].mean()
    avg_rating = result_df['rating'].mean()

    # Overall emotion
    pos_pct = (pos/total)*100
    neg_pct = (neg/total)*100

    if pos_pct >= 70:
        emotion = "😍 Delighted"
    elif pos_pct >= 50:
        emotion = "😊 Satisfied"
    elif neg_pct >= 50:
        emotion = "😞 Disappointed"
    elif neg_pct >= 30:
        emotion = "😤 Frustrated"
    else:
        emotion = "😐 Divided"

    # Print report
    print("\n" + "="*50)
    print(f"  SENTIMENT REPORT: {product_name}")
    print("="*50)
    print(f"  Overall Emotion  : {emotion}")
    print(f"  Sentiment Score  : {round((avg_score + 1) * 50)}/100")
    print(f"  Average Rating   : {round(avg_rating, 1)}/5 ⭐")
    print(f"  Total Reviews    : {total}")
    print(f"\n  Positive  : {round(pos_pct)}%  ({pos} reviews)")
    print(f"  Neutral   : {round((neu/total)*100)}%  ({neu} reviews)")
    print(f"  Negative  : {round(neg_pct)}%  ({neg} reviews)")
    print(f"\n  Top Positive Reviews:")
    top_pos = result_df[result_df['sentiment'] == 'Positive'].nlargest(3, 'compound_score')
    for _, r in top_pos.iterrows():
        print(f"    ✅ {r['review'][:80]}...")
    print(f"\n  Top Negative Reviews:")
    top_neg = result_df[result_df['sentiment'] == 'Negative'].nsmallest(3, 'compound_score')
    for _, r in top_neg.iterrows():
        print(f"    ❌ {r['review'][:80]}...")
    print("="*50)

    # Save results
    filename = product_name.replace(" ", "_").lower() + "_sentiment.csv"
    result_df.to_csv(filename, index=False)
    print(f"\n✅ Saved sentiment results to '{filename}'")

    return result_df

# ── Main ──
print("\n📊 SENTIMENT ANALYZER")

# Find all review CSV files
csv_files = [f for f in os.listdir(".") if f.endswith("_reviews.csv")]

if not csv_files:
    print("❌ No review files found! Run scraper.py first.")
else:
    print("\nWhich product to analyze?\n")
    for i, f in enumerate(csv_files):
        name = f.replace("_reviews.csv", "").replace("_", " ").title()
        print(f"  [{i+1}] {name}")

    choice = int(input("\nEnter number: ")) - 1
    filename = csv_files[choice]
    product_name = filename.replace("_reviews.csv", "").replace("_", " ").title()

    df = pd.read_csv(filename)
    print(f"✅ Loaded {len(df)} reviews")

    analyze_sentiment(product_name, df)