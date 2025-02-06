import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from io import BytesIO  # Import BytesIO for in-memory file handling

# Constants
API_KEY = "a0c1c50cbbbed5659a779e082f9f1f00"  # Your GNews API key
GNEWS_URL = "https://gnews.io/api/v4/search"

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
        "Shell", "BP", "Exxon", "Chevron", "Total", "Conoco", "Schlumberger", 
        "Halliburton", "Baker Hughes", "Equinor", "Petrobras", "Gazprom", 
        "Aramco", "ADNOC", "ENI", "Rosneft", "Repsol", "CNPC", "Sinopec", 
        "CNOOC", "Phillips 66", "Valero Energy", "Marathon Petroleum"
    ],
    "Regional Companies": {
        "India": ["ONGC", "IOC", "BPCL", "HPCL", "RIL", "Cairn"],
        "Pakistan": [
            "OGDCL", "PPL", "MPCL", "PSO", "ARL", "Byco", "NRL", 
            "PARCO", "SNGPL", "SSGC", "Hascol", "Pak LNG", "TOR"
        ],
        "Sri Lanka": ["Ceylon Petroleum Corporation", "Lanka IOC"],
        "Bangladesh": ["Petrobangla", "BAPEX"]
    }
}

DEFAULT_KEYWORDS = [
    "oil", "gas", "energy", "reservoir", "supply", "demand", "exploration", "production", "renewable",
    "petroleum", "natural gas", "refining", "pipeline", "offshore", "onshore", "CCUS", "carbon capture",
    "emissions", "climate", "storage", "drilling", "shale", "LNG", "biofuel", "Shell", "BP", "Exxon", 
    "Chevron", "Total", "Conoco", "Schlumberger", "HAL", "Baker Hughes", "Statoil", "Petrobras", 
    "Gazprom", "Aramco", "ADNOC", "ENI", "Rosneft", "Repsol", "CNPC", "Sinopec", "CNOOC", "ONGC", 
    "IOC", "BPCL", "HPCL", "RIL", "Cairn", "OGDCL", "PPL", "MPCL", "PSO", "ARL", "Byco", "NRL", 
    "PARCO", "SNGPL", "SSGC", "Hascol", "Pak LNG", "TOR", "ExxonMobil", "TotalEnergies", 
    "ConocoPhillips", "Halliburton", "Equinor", "Saudi Aramco", "Eni", "Indian Oil Corporation", 
    "Bharat Petroleum", "Hindustan Petroleum", "Reliance Industries", "Cairn Oil & Gas", 
    "Pakistan Petroleum Limited", "Oil & Gas Development Company Limited", "Mari Petroleum Company Limited", 
    "Pakistan State Oil", "Attock Refinery Limited", "Byco Petroleum Pakistan Limited", 
    "National Refinery Limited", "Pak-Arab Refinery Limited", "Sui Northern Gas Pipelines Limited", 
    "Sui Southern Gas Company Limited", "Hascol Petroleum Limited", "Pak LNG Limited", 
    "Tariq Oil Refinery", "Ceylon Petroleum Corporation", "Lanka IOC", "Petrobangla", "BAPEX", 
    "Phillips 66", "Valero Energy", "Marathon Petroleum"
]

# Helper Functions
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

def fetch_articles(search_query, selected_country, start_date, end_date):
    """Fetch articles from the GNews API."""
    params = {
        "q": search_query,
        "from": start_date,
        "to": end_date,
        "apikey": API_KEY,
        "lang": "en",
        "max": 100  # Maximum number of articles to fetch
    }
    if selected_country != "All Countries":
        params["country"] = selected_country.lower()

    response = requests.get(GNEWS_URL, params=params)
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        data = []
        for article in articles:
            data.append({
                "Title": article.get("title"),
                "Description": article.get("description"),
                "Published At": article.get("publishedAt"),
                "Source": article.get("source", {}).get("name"),
                "URL": article.get("url")
            })
        return data
    else:
        st.error(f"Failed to fetch news. Error: {response.status_code} - {response.text}")
        return None

def display_articles(data, search_query, selected_country):
    """Display articles in a DataFrame and provide a download option."""
    if data:
        df = pd.DataFrame(data)
        st.write(f"### Articles related to '{search_query}' in {selected_country}:")
        st.dataframe(df)

        # Create an in-memory Excel file
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
        output.seek(0)  # Reset the pointer to the beginning of the file

        # Download button
        st.download_button(
            label="Download Articles",
            data=output,
            file_name="news_articles.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.error("No articles found for the selected country and keyword.")

# Streamlit App
def main():
    st.title("Energy and Oil & Gas News Collector")

    # Sidebar for filters and keyword reference
    st.sidebar.header("Search Filters")
    search_query = st.sidebar.text_input("Enter Keywords", value=", ".join(DEFAULT_KEYWORDS))
    selected_country = st.sidebar.selectbox("Select a Country", ["All Countries"] + COUNTRIES)
    start_date = st.sidebar.date_input("Start Date", datetime(2024, 1, 1))
    end_date = st.sidebar.date_input("End Date", datetime.now())

    # Validate dates
    if start_date > end_date:
        st.sidebar.error("Start date cannot be after end date.")
        return

    # Display keyword reference
    display_keyword_reference()

    # Fetch and display articles
    if st.sidebar.button("Fetch News"):
        data = fetch_articles(search_query, selected_country, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        if data is not None:
            display_articles(data, search_query, selected_country)

    # Footer
    st.write("\n---")
    st.write(
        "This app collects the latest news articles related to energy and oil & gas industries, filtered by keywords and countries."
    )

if __name__ == "__main__":
    main()
