import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from io import BytesIO

# API Keys and URLs
NEWSAPI_KEY = "3087034a13564f75bfc769c0046e729c"
NEWSAPI_URL = "https://newsapi.org/v2/everything"
SPARK_ASSIST_API_KEY = "eyJraWQiOiJCVG1JZlI4QkppX1RNMDAtWGhEaF9wR3ZrS0x2YnR2V3BJOXhjWXdfVVpFIiwiYWxnIjoiUlMyNTYifQ.eyJ2ZXIiOjEsImp0aSI6IkFULlJEUElCVkYtRDR4MEdyLUJZcmN0ckhmaG9QdnhUc1F6TE1vWDN6d0xHQzQub2FyMnpuZ29ncWdmVnhVZFo1ZDciLCJpc3MiOiJodHRwczovL3NwZ2xvYmFsLm9rdGEuY29tL29hdXRoMi9kZWZhdWx0IiwiYXVkIjoiYXBpOi8vZGVmYXVsdCIsImlhdCI6MTc0MDA0ODkyNCwiZXhwIjoxNzQwMDUyNTI0LCJjaWQiOiIwb2Fld3gyeGxudE9jMVFUazVkNyIsInVpZCI6IjAwdWxkcTBweXJDZlhjZng5NWQ3Iiwic2NwIjpbIm9mZmxpbmVfYWNjZXNzIiwib3BlbmlkIiwiZW1haWwiLCJwcm9maWxlIl0sImF1dGhfdGltZSI6MTc0MDA0ODkyMywiY291bnRyeSI6IklORElBIiwic3ViIjoic2hhcnVnaC5hQHNwZ2xvYmFsLmNvbSJ9.TOtlEQA3GSrpYoeMJp4m6loJRlDiE1vLBqDw_-fPBjhbAlMZ5kCG99VdD9XVhN6ij-Txvj1_jVjxqKwieLrC8JU7lLMNgy3qI0PAGO1uY2GxpDUjorzOWsdd561PHPgGgz4BxsBKGaHjXo5eFC-gs_orTGhK6EhG5KSOUXFd42jTKU0obcDU23JeqrsFaq9YtVspkrJcpHQ07H-yf0RA7mX5b7Lpuy0SB-D7qP3ao4c9-VjYqbGdgy1OeJJlSMoDHkjyKYexOupVNEcoJT-BS0k1eHlPiikwaF5c26t6TtNa2Ezfg-GNmH-h_ccTMg6hWfK1oXKR2_hmc74nJsSLEA"  # Replace with your Spark Assist API key
SPARK_ASSIST_API_URL = "https://api.sparkassist.com/v1/chat/completions"  # Replace with Spark Assist API URL

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
    """Ensure the query follows API rules (space-separated, max 200 chars)."""
    query = query.strip()  # Remove extra spaces
    query = " ".join(query.split())  # Ensure proper spacing
    return query[:200]  # Trim to 200 characters to prevent errors

def fetch_articles(search_query, start_date, end_date):
    """Fetch articles from the NewsAPI while ensuring valid query formatting."""
    if not search_query.strip():  # Ensure query is not empty
        st.error("Error: Search query is empty. Please enter valid keywords.")
        return None

    params = {
        "q": search_query,
        "from": start_date,
        "to": end_date,
        "apiKey": NEWSAPI_KEY,
        "language": "en",
        "pageSize": 50  # Fetch up to 50 articles
    }

    response = requests.get(NEWSAPI_URL, params=params)
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        data = [
            {
                "Title": article.get("title"),
                "Description": article.get("description"),
                "Content": article.get("content", ""),  # New field
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

def generate_summary_spark_assist(text, max_length=150):
    """Generate a summary using Spark Assist API."""
    if not text.strip():
        return "No content available for summarization."
    
    headers = {
        "Authorization": f"Bearer {SPARK_ASSIST_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openAI-4o",  # Replace with your Spark Assist model name
        "messages": [
            {"role": "system", "content": "Summarize this article into 3 concise bullet points. Focus on key entities, numbers, and outcomes."},
            {"role": "user", "content": text[:3000]}  # Limit input to avoid token limits
        ],
        "max_tokens": max_length
    }

    try:
        response = requests.post(SPARK_ASSIST_API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"].strip()
        else:
            return f"Summary error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Summary error: {str(e)}"

def display_articles(data, search_query, selected_country):
    """Display articles with summaries and download option."""
    if data:
        df = pd.DataFrame(data)
        
        # Add summaries using Spark Assist
        df["Summary"] = df["Content"].apply(
            lambda x: generate_summary_spark_assist(x) if pd.notnull(x) else "No content"
        )
        
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
        st.error("No articles found.")

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
        data = fetch_articles(formatted_query, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        if data:
            display_articles(data, formatted_query, selected_country)

if __name__ == "__main__":
    main()
