# Mobile Phone Sentiment Analyzer

## Project Overview

A Python-based web application that collects customer reviews of mobile phones from Flipkart and analyzes their sentiment using Natural Language Processing (NLP).

## Features

- Collects mobile phone reviews using Selenium and BeautifulSoup.
- Cleans and preprocesses review data using Pandas and Regular Expressions.
- Classifies reviews into Positive, Negative, and Neutral categories using VADER sentiment analysis.
- Displays sentiment distribution through pie charts.
- Visualizes rating distributions.
- Generates word clouds from customer reviews.
- Displays top customer reviews.
- Provides an interactive dashboard using Streamlit.

## Technologies Used

- **Programming Language:** Python
- **Web Framework:** Streamlit
- **Web Scraping:** Selenium, BeautifulSoup
- **Data Processing:** Pandas
- **Sentiment Analysis:** NLTK (VADER)
- **Visualization:** Matplotlib, WordCloud

## Project Structure

| File | Description |
|---|---|
| `app.py` | Main Streamlit application |
| `scraper.py` | Collects mobile phone reviews |
| `sentiment.py` | Performs sentiment analysis |
| `visualize.py` | Generates visualizations |

## How to Run the Project

### 1. Install dependencies

```bash
pip install streamlit pandas matplotlib wordcloud nltk selenium webdriver-manager beautifulsoup4
```

### 2. Run the application

```bash
streamlit run app.py
```

## Results

The application analyzes customer reviews of different mobile phone models and presents sentiment classifications and visualizations to help understand customer opinions.

