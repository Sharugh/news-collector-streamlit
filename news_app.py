import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# Your API Key (Never share this publicly)
api_key = "32c6b5f1df1642de8ff199fbe2d11f9d"

# Function to fetch news articles based on user inputs
def fetch_news(api_key, start_date, end_date, country, keywords):
    url = f'https://newsapi.org/v2/everything?q={keywords}&from={start_date}&to={end_date}&language=en&apiKey={api_key}&pageSize=100'
    
    if country:
        url += f"&country={country}"
    
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['articles']
    else:
        st.error(f"Error fetching data: {response.status_code}")
        return []

# Function to display articles
def display_articles(articles):
    data = []
    for article in articles:
        title = article['title']
        description = article['description'] if article['description'] else 'No description available.'
        url = article['url']
        source = article['source']['name']
        data.append([title, description, source, url])
    
    df = pd.DataFrame(data, columns=["Title", "Description", "Source", "URL"])
    st.write(df)

# App title
st.title("Oil & Gas News Collector")

# Date input
start_date = st.date_input("Start Date", datetime.today() - timedelta(days=30))
end_date = st.date_input("End Date", datetime.today())

# Country selection dropdown
country = st.selectbox("Select Country", ["", "us", "gb", "ca", "in", "au", "de", "fr", "jp"])

# Keywords search input
keywords_input = st.text_input("Search by Keyword", "oil and gas, reservoir, exploration, drilling, supply, demand, carbon capture, energy transition, energy, pakistan,")

# Fetching articles when user clicks the button
if st.button('Fetch News'):
    articles = fetch_news(api_key, start_date, end_date, country, keywords_input)
    if articles:
        display_articles(articles)
