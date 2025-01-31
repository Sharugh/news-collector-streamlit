import streamlit as st
import pandas as pd
import requests

API_KEY = "32c6b5f1df1642de8ff199fbe2d11f9d"

# Country List
countries = [
    "Afghanistan", "Bangladesh", "Bhutan", "India", "Maldives", "Nepal", "Pakistan", "Sri Lanka", 
    "United States", "China", "Russia", "Japan", "Germany", "United Kingdom", "France", "Italy", "Canada", "Australia",
    "Brazil", "Mexico", "Indonesia", "South Korea", "Saudi Arabia", "South Africa", "Turkey", "Argentina", "Spain",
    "Netherlands", "Sweden", "Switzerland", "Singapore", "Malaysia", "Thailand", "Philippines", "Vietnam", "Nigeria",
    "Egypt", "United Arab Emirates", "Qatar", "Kuwait", "Norway", "Denmark", "Poland", "Belgium", "Austria",
    "Czech Republic", "Finland", "Portugal", "New Zealand", "Greece", "Chile", "Colombia", "Peru", "Israel"
]

# Keywords
keywords = [
    "oil", "gas", "energy", "reservoir", "supply", "demand", "exploration", "production", "offshore", "onshore",
    "refinery", "pipeline", "LNG", "natural gas", "fossil fuel", "petroleum", "hydrocarbon", "renewable energy",
    "carbon capture", "emissions", "drilling", "upstream", "midstream", "downstream", "reserves", "EOR (Enhanced Oil Recovery)"
]

# Streamlit App
st.title("Oil & Gas News Collector")
st.sidebar.header("Search Filters")

# Country Selection
selected_country = st.sidebar.selectbox("Select a country", countries)

# Keyword Search
search_query = st.sidebar.text_input("Search for a specific keyword or phrase", "")

# Input Date Range
start_date = st.sidebar.date_input("Start date")
end_date = st.sidebar.date_input("End date")

# Fetch Articles
if st.sidebar.button("Fetch News"):
    url = f"https://newsapi.org/v2/everything?q={search_query}&from={start_date}&to={end_date}&apiKey={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        if articles:
            data = []
            for article in articles[:100]:  # Limit to 100 articles
                if selected_country.lower() in article.get("description", "").lower():
                    data.append({
                        "Title": article.get("title"),
                        "Description": article.get("description"),
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
