import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from io import BytesIO

# API Keys
NEWSAPI_KEY = "3087034a13564f75bfc769c0046e729c"
NEWSAPI_URL = "https://newsapi.org/v2/everything"

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
        "India": ["ONGC", "Indian Oil Corporation (IOC)", "Bharat Petroleum (BPCL)", "Hindustan Petroleum (HPCL)", "Reliance Industries (RIL)", "Cairn Oil & Gas"],
        "Pakistan": [
            "Oil & Gas Development Company Limited (OGDCL)", "Pakistan Petroleum Limited (PPL)",
            "Mari Petroleum Company Limited (MPCL)", "Pakistan State Oil (PSO)", "Attock Refinery Limited (ARL)",
            "Byco Petroleum Pakistan Limited (Byco)", "National Refinery Limited (NRL)", "Pak-Arab Refinery Limited (PARCO)",
            "Sui Northern Gas Pipelines Limited (SNGPL)", "Sui Southern Gas Company Limited (SSGC)", "Hascol Petroleum Limited",
            "Pak LNG Limited", "Tariq Oil Refinery (TOR)"
        ],
        "Sri Lanka": ["Ceylon Petroleum Corporation", "Lanka IOC"],
        "Bangladesh": ["Petrobangla", "Bangladesh Petroleum Exploration and Production Company Limited (BAPEX)"]
    }
}

def format_query(query):
    """Ensure query follows API rules (space-separated, max 200 chars)."""
    query = query.strip()  
    query = " ".join(query.split())  
    return query[:200]  

def summarize_text_spark_assist(text):
    """Summarize article description using Spark Assist API."""
    if not text or len(text) < 50:
        return "No summary available"

    payload = {
        "model": "openAI-4o",
        "messages": [{"role": "user", "content": f"Summarize this article: {text}"}],
        "temperature": 0.5
    }

    headers = {"Authorization": f"Bearer {SPARK_ASSIST_API_KEY}", "Content-Type": "application/json"}

    try:
        response = requests.post(SPARK_ASSIST_URL, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No summary available")
        else:
            return f"Error in summarization: {response.status_code}"
    except Exception as e:
        return f"Summarization failed: {e}"

def fetch_articles(search_query, start_date, end_date):
    """Fetch articles from NewsAPI."""
    if not search_query.strip():
        st.error("Error: Search query is empty. Please enter valid keywords.")
        return None

    params = {
        "q": search_query,
        "from": start_date,
        "to": end_date,
        "apiKey": NEWSAPI_KEY,
        "language": "en",
        "pageSize": 100  
    }

    response = requests.get(NEWSAPI_URL, params=params)
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        data = [
            {
                "Title": article.get("title"),
                "Description": article.get("description"),
                "Published At": article.get("publishedAt"),
                "Source": article.get("source", {}).get("name"),
                "URL": article.get("url"),
                "Summary": summarize_text_spark_assist(article.get("description"))
            }
            for article in articles
        ]
        return data
    else:
        st.error(f"Failed to fetch news. Error {response.status_code}: {response.text}")
        return None

def display_articles(data, search_query, selected_country):
    """Display articles and enable downloading."""
    if data:
        df = pd.DataFrame(data)
        st.write(f"### News related to '{search_query}' in {selected_country}:")
        st.dataframe(df)

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
        st.error("No articles found.")

def display_keyword_reference():
    """Display keywords in sidebar."""
    st.sidebar.title("Keyword Reference")
    for category, items in KEYWORDS.items():
        if isinstance(items, dict):
            with st.sidebar.expander(category):
                for region, companies in items.items():
                    st.write(f"**{region}:**")
                    st.write(", ".join(companies))
        else:
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
        data = fetch_articles(formatted_query, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        if data:
            display_articles(data, formatted_query, selected_country)

if __name__ == "__main__":
    main()
