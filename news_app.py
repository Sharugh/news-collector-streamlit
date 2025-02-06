import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from io import BytesIO

# Constants
API_KEY = "32c6b5f1df1642de8ff199fbe2d11f9d"  # Replace with your valid NewsAPI key

COUNTRIES = [
    "Afghanistan", "Bangladesh", "Bhutan", "India", "Maldives", "Nepal", "Pakistan", "Sri Lanka",
    "United States", "Canada", "United Kingdom", "Germany", "France", "Italy", "Spain", "Russia",
    "China", "Japan", "South Korea", "Australia", "New Zealand", "Brazil", "Mexico", "South Africa",
    "Nigeria", "Egypt", "Turkey", "Saudi Arabia", "United Arab Emirates", "Argentina", "Colombia",
    "Indonesia", "Thailand", "Malaysia", "Singapore", "Vietnam", "Philippines", "Netherlands",
    "Sweden", "Norway", "Denmark", "Switzerland", "Poland", "Czech Republic", "Austria",
    "Belgium", "Portugal", "Greece", "Hungary", "Finland", "Ireland"
]

DEFAULT_KEYWORDS = [
    "oil", "gas", "energy", "reservoir", "supply", "demand", "exploration", "production", "renewable",
    "petroleum", "natural gas", "refining", "pipeline", "offshore", "onshore", "CCUS", "carbon capture",
    "emissions", "climate", "storage", "drilling", "shale", "LNG", "biofuel", "Shell", "BP", "Exxon", 
    "Chevron", "Total", "Conoco", "Schlumberger", "Halliburton", "Baker Hughes", "Equinor", "Petrobras",
    "Gazprom", "Aramco", "ADNOC", "ENI", "Rosneft", "Repsol", "CNPC", "Sinopec", "CNOOC"
]

# Helper Functions
def fetch_articles(search_query, start_date, end_date):
    """Fetch news articles from NewsAPI with error handling."""
    url = f"https://newsapi.org/v2/everything?q={search_query}&from={start_date}&to={end_date}&language=en&sortBy=publishedAt&apiKey={API_KEY}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise error for HTTP errors (4xx, 5xx)
        articles = response.json().get("articles", [])

        if not articles:
            st.warning("No articles found for the given search parameters.")
            return None

        data = []
        for article in articles[:100]:  # Limit to 100 articles
            data.append({
                "Title": article.get("title"),
                "Description": article.get("description"),
                "Published At": article.get("publishedAt"),
                "Source": article.get("source", {}).get("name"),
                "URL": article.get("url")
            })
        return pd.DataFrame(data)

    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        st.error(f"Request error occurred: {req_err}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

    return None

def convert_df_to_excel(df):
    """Convert a DataFrame to an Excel file in memory."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    processed_data = output.getvalue()
    return processed_data

# Streamlit App
def main():
    st.title("🔍 Energy & Oil & Gas News Collector")

    # Sidebar Filters
    st.sidebar.header("🔎 Search Filters")
    search_query = st.sidebar.text_area("Enter Keywords (comma-separated)", value=", ".join(DEFAULT_KEYWORDS))
    start_date = st.sidebar.date_input("Start Date", datetime(2024, 1, 1))
    end_date = st.sidebar.date_input("End Date", datetime.now())

    # Validate Dates
    if start_date > end_date:
        st.sidebar.error("⚠️ Start date cannot be after end date.")
        return

    # Fetch and Display Articles
    if st.sidebar.button("📢 Fetch News"):
        st.info("Fetching latest news articles... Please wait.")
        data = fetch_articles(search_query, start_date, end_date)
        if data is not None:
            st.write(f"### 📌 Articles related to `{search_query}`:")
            st.dataframe(data)

            # Download Button
            excel_data = convert_df_to_excel(data)
            st.download_button(
                label="📥 Download Articles (Excel)",
                data=excel_data,
                file_name="news_articles.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # Footer
    st.write("\n---")
    st.write("📌 This app collects the latest news articles related to energy and oil & gas industries, filtered by keywords.")

if __name__ == "__main__":
    main()
