import streamlit as st
import requests
import pandas as pd

# API Key
API_KEY = "32c6b5f1df1642de8ff199fbe2d11f9d"
BASE_URL = "https://newsapi.org/v2/everything"

# Function to fetch news
def fetch_news(keyword, from_date, to_date, page_size=100):
    articles_list = []
    page = 1

    while True:
        params = {
            'q': keyword,
            'from': from_date,
            'to': to_date,
            'sortBy': 'relevancy',
            'pageSize': page_size,
            'page': page,
            'apiKey': API_KEY
        }

        response = requests.get(BASE_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            if not articles:
                break
            articles_list.extend(articles)
            page += 1
            if page > data['totalResults'] // page_size + 1:
                break
        else:
            st.error(f"Error: {response.status_code}, {response.json()}")
            break

    return articles_list

# Streamlit Interface
st.title("Energy, Oil & Gas News Collector")
st.write("Fetch the latest news articles in the energy, oil, and gas industry.")

# User Inputs
keyword = st.text_input("Enter keyword(s) (e.g., energy OR oil AND gas)", "energy OR oil AND gas")
from_date = st.date_input("Start Date")
to_date = st.date_input("End Date")

# Fetch and Display Articles
if st.button("Fetch News"):
    with st.spinner("Fetching articles..."):
        articles = fetch_news(keyword, from_date, to_date)
        if articles:
            data = [{'Source': article['source']['name'],
                     'Title': article['title'],
                     'Description': article['description'],
                     'URL': article['url'],
                     'Published At': article['publishedAt']} for article in articles]
            df = pd.DataFrame(data)
            st.success(f"Fetched {len(data)} articles.")
            st.dataframe(df)
            # Option to Download as Excel
            st.download_button(
                label="Download Articles as Excel",
                data=df.to_excel(index=False, engine='openpyxl'),
                file_name="energy_oil_gas_news.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("No articles found for the given timeline.")
