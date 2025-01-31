import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# API Key
API_KEY = "32c6b5f1df1642de8ff199fbe2d11f9d"

# Country List
COUNTRIES = [
    "Afghanistan", "Bangladesh", "Bhutan", "India", "Maldives", "Nepal", "Pakistan", "Sri Lanka",
    "United States", "Canada", "United Kingdom", "Germany", "France", "Italy", "Spain", "Russia",
    "China", "Japan", "South Korea", "Australia", "New Zealand", "Brazil", "Mexico", "South Africa",
    "Nigeria", "Egypt", "Turkey", "Saudi Arabia", "United Arab Emirates", "Argentina", "Colombia",
    "Indonesia", "Thailand", "Malaysia", "Singapore", "Vietnam", "Philippines", "Netherlands",
    "Sweden", "Norway", "Denmark", "Switzerland", "Poland", "Czech Republic", "Austria",
    "Belgium", "Portugal", "Greece", "Hungary", "Finland", "Ireland"
]

# Frequent Keywords in Oil and Gas Industry
DEFAULT_KEYWORDS = [
    "oil", "gas", "energy", "reservoir", "supply", "demand", "exploration", "production", "renewable",
    "petroleum", "natural gas", "refining", "pipeline", "offshore", "onshore", "CCUS", "carbon capture",
    "emissions", "climate", "storage", "drilling", "shale", "LNG", "biofuel",  "oil", "gas", "energy", "reservoir", "supply", "demand",
    "Shell", "BP", "Exxon", "Chevron", "Total", "Conoco", "Schlumberger", "HAL",
    "Baker Hughes", "Statoil", "Petrobras", "Gazprom", "Aramco", "ADNOC", "ENI",
    "Rosneft", "Repsol", "CNPC", "Sinopec", "CNOOC", "ONGC", "IOC", "BPCL",
    "HPCL", "RIL", "Cairn", "OGDCL", "PPL", "MPCL", "PSO", "ARL", "Byco",
    "NRL", "PARCO", "SNGPL", "SSGC", "Hascol", "Pak LNG", "TOR" , "oil", "gas", "energy", "reservoir", "supply", "demand",
    "Shell", "BP", "ExxonMobil", "Chevron", "TotalEnergies",
    "ConocoPhillips", "Schlumberger", "Halliburton", "Baker Hughes",
    "Equinor", "Petrobras", "Gazprom", "Saudi Aramco", "ADNOC", "Eni",
    "Rosneft", "Repsol", "CNPC", "Sinopec", "CNOOC",
    "ONGC", "Indian Oil Corporation", "Bharat Petroleum", "Hindustan Petroleum",
    "Reliance Industries", "Cairn Oil & Gas",
    "Pakistan Petroleum Limited", "Oil & Gas Development Company Limited",
    "Mari Petroleum Company Limited", "Pakistan State Oil", "Attock Refinery Limited",
    "Byco Petroleum Pakistan Limited", "National Refinery Limited",
    "Pak-Arab Refinery Limited", "Sui Northern Gas Pipelines Limited",
    "Sui Southern Gas Company Limited", "Hascol Petroleum Limited", 
    "Pak LNG Limited", "Tariq Oil Refinery",
    "Ceylon Petroleum Corporation", "Lanka IOC", "Petrobangla",
    "BAPEX", "Phillips 66", "Valero Energy", "Marathon Petroleum"
]

# Streamlit App Setup
st.title("Energy and Oil & Gas News Collector")

# User Inputs
st.sidebar.header("Search Filters")
search_query = st.sidebar.text_input("Enter Keywords", value=", ".join(DEFAULT_KEYWORDS))
selected_country = st.sidebar.selectbox("Select a Country", ["All Countries"] + COUNTRIES)
start_date = st.sidebar.date_input("Start Date", datetime(2024, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime.now())

# Validate Dates
if start_date > end_date:
    st.sidebar.error("Start date cannot be after end date.")

# Fetch Articles
if st.sidebar.button("Fetch News"):
    url = f"https://newsapi.org/v2/everything?q={search_query}&from={start_date}&to={end_date}&apiKey={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        if articles:
            data = []
            for article in articles[:100]:  # Limit to 100 articles
                description = article.get("description", "")
                # Ensure the description is a string and filter by country
                if selected_country == "All Countries" or (
                    description and selected_country.lower() in description.lower()
                ):
                    data.append({
                        "Title": article.get("title"),
                        "Description": description,
                        "Published At": article.get("publishedAt"),
                        "Source": article.get("source", {}).get("name"),
                        "URL": article.get("url")
                    })
            if data:
                df = pd.DataFrame(data)
                st.write(f"### Articles related to '{search_query}' in {selected_country}:")
                st.dataframe(df)
                st.download_button(
                    label="Download Articles",
                    data=df.to_excel(index=False, engine="openpyxl"),
                    file_name="news_articles.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.error("No articles found for the selected country and keyword.")
        else:
            st.error("No articles found for the selected filters.")
    else:
        st.error("Failed to fetch news. Please check your API key or try again later.")

# Footer
st.write("\n---")
st.write(
    "This app collects the latest news articles related to energy and oil & gas industries, filtered by keywords and countries."
)

