import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from io import BytesIO 

API_KEY = "3087034a13564f75bfc769c0046e729c"  
NEWSAPI_URL = "https://newsapi.org/v2/everything"  # Correct NewsAPI endpoint

COUNTRIES = [
    "Afghanistan", "Bangladesh", "Bhutan", "India", "Maldives", "Nepal", "Pakistan", "Sri Lanka",
    "United States", "Canada", "United Kingdom", "Germany", "France", "Italy", "Spain", "Russia",
    "China", "Japan", "South Korea", "Australia", "New Zealand", "Brazil", "Mexico", "South Africa",
    "Nigeria", "Egypt", "Turkey", "Saudi Arabia", "United Arab Emirates", "Argentina", "Colombia",
    "Indonesia", "Thailand", "Malaysia", "Singapore", "Vietnam", "Philippines", "Netherlands",
    "Sweden", "Norway", "Denmark", "Switzerland", "Poland", "Czech Republic", "Austria",
    "Belgium", "Portugal", "Greece", "Hungary", "Finland", "Ireland"
]

KEYWORDS = {
    "General Terms": [
        "oil", "gas", "energy", "reservoir", "supply", "demand", "exploration", 
        "production", "renewable", "petroleum", "natural gas", "refining", 
        "pipeline", "offshore", "onshore", "CCUS", "carbon capture", 
        "emissions", "climate", "storage", "drilling", "shale", "LNG", "biofuel"
    ],
    "Global Companies": [
        "Shell", "BP", "ExxonMobil", "Chevron", "TotalEnergies", "ConocoPhillips", 
        "Schlumberger", "Halliburton", "Baker Hughes", "Equinor", "Petrobras", "Gazprom", 
        "Saudi Aramco", "ADNOC", "ENI", "Rosneft", "Repsol", "CNPC", "Sinopec", "CNOOC", 
        "Phillips 66", "Valero Energy", "Marathon Petroleum"
    ],
    "Regional Companies": {
        "India": ["ONGC", "Indian Oil Corporation (IOC)", "Bharat Petroleum (BPCL)", "Hindustan Petroleum (HPCL)", "Reliance Industries (RIL)", "Cairn Oil & Gas"],
        "Pakistan": [
            "Oil & Gas Development Company Limited (OGDCL)", "Pakistan Petroleum Limited (PPL)", "Mari Petroleum Company Limited (MPCL)", 
            "Pakistan State Oil (PSO)", "Attock Refinery Limited (ARL)", "Byco Petroleum Pakistan Limited (Byco)", 
            "National Refinery Limited (NRL)", "Pak-Arab Refinery Limited (PARCO)", "Sui Northern Gas Pipelines Limited (SNGPL)", 
            "Sui Southern Gas Company Limited (SSGC)", "Hascol Petroleum Limited", "Pak LNG Limited", "Tariq Oil Refinery (TOR)"
        ],
        "Sri Lanka": ["Ceylon Petroleum Corporation", "Lanka IOC"],
        "Bangladesh": ["Petrobangla", "Bangladesh Petroleum Exploration and Production Company Limited (BAPEX)"]
    }
}

def format_query(query):
    """Ensure the query follows API rules (space-separated, max 200 chars)."""
    query = query.strip()  # Remove extra spaces
    query = " ".join(query.split())  # Ensure proper spacing
    return query[:200]  # Trim to 200 characters to prevent errors

def fetch_articles(search_query, selected_country, start_date, end_date):
    """Fetch articles from the NewsAPI while ensuring valid query formatting."""
    if not search_query.strip():  # Ensure query is not empty
        st.error("Error: Search query is empty. Please enter valid keywords.")
        return None

    params = {
        "q": search_query,
        "from": start_date,
        "to": end_date,
        "apiKey": API_KEY,
        "language": "en",
        "pageSize": 50  # Fetch up to 50 articles
    }
    if selected_country != "All Countries":
        params["country"] = selected_country.lower()

    response = requests.get(NEWSAPI_URL, params=params)
    
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        data = [
            {
                "Title": article.get("title"),
                "Description": article.get("description"),
                "Published At": article.get("publishedAt"),
                "Source": article.get("source", {}).get("name"),
                "URL": article.get("url")
            }
            for article in articles
        ]
        return data
    else:
        st.error(f"Failed to fetch news. Error {response.status_code}: {response.text}")
        return None

def display_articles(data, search_query, selected_country):
    """Display articles in a table with a download option."""
    if data:
        df = pd.DataFrame(data)
        st.write(f"### News related to '{search_query}' in {selected_country}:")
        st.dataframe(df)

        # Download as Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
        output.seek(0)

        st.download_button(
            label="Download Articles",
            data=output,
            file_name="news_articles.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.error("No articles found for the selected country and keyword.")

def display_keyword_reference():
    """Display keyword reference in the sidebar."""
    st.sidebar.title("Keyword Reference")
    for category, items in KEYWORDS.items():
        if isinstance(items, dict):  # Region-based companies
            with st.sidebar.expander(category):
                for region, companies in items.items():
                    st.write(f"**{region}:**")
                    st.write(", ".join(companies))
        else:  # General or Global Companies
            with st.sidebar.expander(category):
                st.write(", ".join(items))

def main():
    st.title("Energy and Oil & Gas News Collector")

    st.sidebar.header("Search Filters")
    search_query = st.sidebar.text_area("Enter Keywords (Space-Separated)", "") 

    selected_country = st.sidebar.selectbox("Select a Country", ["All Countries"] + COUNTRIES)
    start_date = st.sidebar.date_input("Start Date", datetime(2024, 1, 1))
    end_date = st.sidebar.date_input("End Date", datetime.now())

    if start_date > end_date:
        st.sidebar.error("Start date cannot be after the end date.")
        return

    display_keyword_reference()

    if st.sidebar.button("Fetch News"):
        formatted_query = format_query(search_query)
        data = fetch_articles(formatted_query, selected_country, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        if data:
            display_articles(data, formatted_query, selected_country)

if __name__ == "__main__":
    main()
