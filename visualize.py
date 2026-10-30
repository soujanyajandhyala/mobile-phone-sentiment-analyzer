import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from wordcloud import WordCloud
import os

def load_sentiment_files():
    files = [f for f in os.listdir(".") if f.endswith("_sentiment.csv")]
    return files

def plot_emotion_summary(df, product_name):
    total = len(df)
    pos = len(df[df['sentiment'] == 'Positive'])
    neu = len(df[df['sentiment'] == 'Neutral'])
    neg = len(df[df['sentiment'] == 'Negative'])

    labels = ['Positive', 'Neutral', 'Negative']
    sizes = [pos, neu, neg]
    colors = ['#639922', '#888780', '#E24B4A']
    explode = (0.05, 0, 0)

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle(f'Sentiment Report — {product_name}', fontsize=16, fontweight='bold')

    # Chart 1 — Pie chart
    axes[0].pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                explode=explode, startangle=90)
    axes[0].set_title('Overall Sentiment Split')

    # Chart 2 — Bar chart of ratings
    rating_counts = df['rating'].value_counts().sort_index()
    bar_colors = ['#E24B4A', '#E24B4A', '#888780', '#639922', '#639922']
    axes[1].bar(rating_counts.index, rating_counts.values, color=bar_colors[:len(rating_counts)])
    axes[1].set_title('Rating Distribution')
    axes[1].set_xlabel('Rating (out of 5)')
    axes[1].set_ylabel('Number of Reviews')
    axes[1].set_xticks([1, 2, 3, 4, 5])

    # Chart 3 — Sentiment score gauge
    avg_score = df['compound_score'].mean()
    normalized = (avg_score + 1) * 50  # convert to 0-100
    gauge_colors = ['#E24B4A', '#EF9F27', '#639922']
    gauge_labels = ['Negative\n(0-40)', 'Neutral\n(40-60)', 'Positive\n(60-100)']
    axes[2].barh(['Score'], [40], color='#E24B4A', height=0.3)
    axes[2].barh(['Score'], [20], left=40, color='#EF9F27', height=0.3)
    axes[2].barh(['Score'], [40], left=60, color='#639922', height=0.3)
    axes[2].axvline(x=normalized, color='black', linewidth=3, linestyle='--')
    axes[2].set_xlim(0, 100)
    axes[2].set_title(f'Sentiment Score: {round(normalized)}/100')
    axes[2].set_xlabel('Score')

    plt.tight_layout()
    filename = product_name.replace(" ", "_").lower() + "_chart.png"
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.show()
    print(f"✅ Chart saved as '{filename}'")

def plot_wordcloud(df, product_name):
    # Positive wordcloud
    pos_text = " ".join(df[df['sentiment'] == 'Positive']['review'].tolist())
    neg_text = " ".join(df[df['sentiment'] == 'Negative']['review'].tolist())

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle(f'Word Cloud — {product_name}', fontsize=16, fontweight='bold')

    if pos_text.strip():
        wc_pos = WordCloud(width=600, height=400,
                          background_color='white',
                          colormap='Greens',
                          max_words=50).generate(pos_text)
        axes[0].imshow(wc_pos, interpolation='bilinear')
        axes[0].set_title('Words in Positive Reviews', color='#3B6D11')
        axes[0].axis('off')

    if neg_text.strip():
        wc_neg = WordCloud(width=600, height=400,
                          background_color='white',
                          colormap='Reds',
                          max_words=50).generate(neg_text)
        axes[1].imshow(wc_neg, interpolation='bilinear')
        axes[1].set_title('Words in Negative Reviews', color='#A32D2D')
        axes[1].axis('off')
    else:
        axes[1].text(0.5, 0.5, 'Not enough\nnegative reviews',
                    ha='center', va='center', fontsize=14)
        axes[1].axis('off')

    plt.tight_layout()
    filename = product_name.replace(" ", "_").lower() + "_wordcloud.png"
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.show()
    print(f"✅ Wordcloud saved as '{filename}'")

def compare_products():
    files = [f for f in os.listdir(".") if f.endswith("_sentiment.csv")]
    if len(files) < 2:
        print("❌ Need at least 2 products to compare!")
        return

    names, scores, pos_pcts, ratings = [], [], [], []

    for f in files:
        df = pd.read_csv(f)
        name = f.replace("_sentiment.csv","").replace("_"," ").title()
        avg = df['compound_score'].mean()
        score = round((avg + 1) * 50)
        pos_pct = round(len(df[df['sentiment']=='Positive'])/len(df)*100)
        avg_rating = df['rating'].mean()
        names.append(name)
        scores.append(score)
        pos_pcts.append(pos_pct)
        ratings.append(avg_rating)

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle('Product Comparison — Sentiment Analysis', fontsize=16, fontweight='bold')

    colors = ['#185FA5', '#639922', '#993C1D', '#534AB7', '#854F0B'][:len(names)]

    # Chart 1 — Sentiment scores
    bars = axes[0].bar(names, scores, color=colors)
    axes[0].set_title('Sentiment Score (0-100)')
    axes[0].set_ylabel('Score')
    axes[0].set_ylim(0, 100)
    for bar, score in zip(bars, scores):
        axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    str(score), ha='center', fontweight='bold')
    axes[0].tick_params(axis='x', rotation=15)

    # Chart 2 — Positive percentage
    bars2 = axes[1].bar(names, pos_pcts, color=colors)
    axes[1].set_title('Positive Reviews %')
    axes[1].set_ylabel('Percentage')
    axes[1].set_ylim(0, 100)
    for bar, pct in zip(bars2, pos_pcts):
        axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{pct}%', ha='center', fontweight='bold')
    axes[1].tick_params(axis='x', rotation=15)

    # Chart 3 — Average rating
    bars3 = axes[2].bar(names, ratings, color=colors)
    axes[2].set_title('Average Rating (out of 5)')
    axes[2].set_ylabel('Rating')
    axes[2].set_ylim(0, 5)
    for bar, r in zip(bars3, ratings):
        axes[2].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                    str(round(r, 1)), ha='center', fontweight='bold')
    axes[2].tick_params(axis='x', rotation=15)

    plt.tight_layout()
    plt.savefig("comparison_chart.png", dpi=150, bbox_inches='tight')
    plt.show()
    print("✅ Comparison chart saved as 'comparison_chart.png'")

# ── Main ──
print("\n📊 VISUALIZATION TOOL")
print("="*40)
print("  [1] Analyze one product")
print("  [2] Compare all products")
print("="*40)

choice = input("\nEnter choice: ").strip()

if choice == "1":
    files = load_sentiment_files()
    print("\nSelect product:\n")
    for i, f in enumerate(files):
        name = f.replace("_sentiment.csv","").replace("_"," ").title()
        print(f"  [{i+1}] {name}")
    sel = int(input("\nEnter number: ")) - 1
    filename = files[sel]
    product_name = filename.replace("_sentiment.csv","").replace("_"," ").title()
    df = pd.read_csv(filename)
    plot_emotion_summary(df, product_name)
    plot_wordcloud(df, product_name)

elif choice == "2":
    compare_products()