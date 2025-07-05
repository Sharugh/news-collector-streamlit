import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from io import BytesIO

# Configuration
NEWSAPI_KEY = "3087034a13564f75bfc769c0046e729c"
NEWSAPI_URL = "https://newsapi.org/v2/everything"

# Constants
COUNTRIES = [
    "Afghanistan", "Bangladesh", "Bhutan", "India", "Maldives", "Nepal", "Pakistan", "Sri Lanka",
    "United States", "Canada", "United Kingdom", "Germany", "France", "Italy", "Spain", "Russia",
    "China", "Japan", "South Korea", "Australia", "New Zealand", "Brazil", "Mexico", "South Africa",
    "Nigeria", "Egypt", "Turkey", "Saudi Arabia", "United Arab Emirates", "Argentina", "Colombia",
    "Indonesia", "Thailand", "Malaysia", "Singapore", "Vietnam", "Philippines", "Netherlands",
    "Sweden", "Norway", "Denmark", "Switzerland", "Poland", "Czech Republic", "Austria", "Belgium",
    "Portugal", "Greece", "Hungary", "Finland", "Ireland"
]

KEYWORDS = {
    "General Terms": [
        "oil", "gas", "energy", "reservoir", "supply", "demand", "exploration", "production",
        "renewable", "petroleum", "natural gas", "refining", "pipeline", "offshore", "onshore",
        "CCUS", "carbon capture", "emissions", "climate", "storage", "drilling", "shale", "LNG", "biofuel", "India Energy Week", "IEW"
    ],
    "Global Companies": [
        "Shell", "BP", "ExxonMobil", "Chevron", "TotalEnergies", "ConocoPhillips", "Schlumberger",
        "Halliburton", "Baker Hughes", "Equinor", "Petrobras", "Gazprom", "Saudi Aramco", "ADNOC",
        "ENI", "Rosneft", "Repsol", "CNPC", "Sinopec", "CNOOC", "Phillips 66", "Valero Energy",
        "Marathon Petroleum"
    ],
    "Regional Companies": {
        "India": ["ONGC", "Indian Oil Corporation (IOC)", "BPCL", "HPCL", "Reliance", "Cairn Oil & Gas"],
        "Pakistan": ["OGDCL", "PPL", "MPCL", "PSO", "ARL", "Byco", "NRL", "PARCO", "SNGPL", "SSGC", "Hascol", "Pak LNG", "TOR"],
        "Sri Lanka": ["Ceylon Petroleum", "Lanka IOC"],
        "Bangladesh": ["Petrobangla", "BAPEX"]
    }
}

def format_query(query):
    return " ".join(query.strip().split())[:200]

def fetch_articles(search_query, start_date, end_date):
    params = {
        "q": search_query,
        "from": start_date,
        "to": end_date,
        "apiKey": NEWSAPI_KEY,
        "language": "en",
        "pageSize": 100
    }
    try:
        response = requests.get(NEWSAPI_URL, params=params)
        if response.status_code != 200:
            st.error(f"Failed to fetch news. {response.status_code}: {response.text}")
            return []
        articles = response.json().get("articles", [])
        return [
            {
                "Title": a.get("title"),
                "Description": a.get("description"),
                "Published At": a.get("publishedAt"),
                "Source": a.get("source", {}).get("name"),
                "URL": a.get("url")
            } for a in articles
        ]
    except Exception as e:
        st.error(f"API request failed: {e}")
        return []

def display_articles(data, query, country):
    if not data:
        st.warning("No articles found.")
        return
    df = pd.DataFrame(data)
    st.write(f"### News for '{query}' in {country}")
    st.dataframe(df)

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    st.download_button(
        "Download as Excel",
        data=output,
        file_name="news_articles.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

def display_keyword_reference():
    st.sidebar.title("Keyword Reference")
    for category, items in KEYWORDS.items():
        with st.sidebar.expander(category):
            if isinstance(items, dict):
                for region, names in items.items():
                    st.markdown(f"**{region}:** {', '.join(names)}")
            else:
                st.write(", ".join(items))

# Main App
def main():
    st.set_page_config(page_title="Energy & Oil News Dashboard", layout="wide")
    st.title("📰 Energy and Oil & Gas News Collector")
    st.sidebar.header("🔍 Search Filters")

    query = st.sidebar.text_area("Keywords (space-separated)", "")
    country = st.sidebar.selectbox("Country", ["All Countries"] + COUNTRIES)
    start_date = st.sidebar.date_input("Start Date", datetime(2024, 1, 1))
    end_date = st.sidebar.date_input("End Date", datetime.now())

    if start_date > end_date:
        st.sidebar.error("Start date cannot be after end date.")
        return

    display_keyword_reference()

    if st.sidebar.button("Fetch News"):
        formatted_query = format_query(query)
        if not formatted_query:
            st.error("Please enter at least one keyword.")
            return
        data = fetch_articles(formatted_query, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        display_articles(data, formatted_query, country)

if __name__ == "__main__":
    main()
