import streamlit as st
import requests

# API Configuration
NEWS_API_URL = "https://newsapi.org/v2/everything"
API_KEY = "32c6b5f1df1642de8ff199fbe2d11f9d"  # Replace with your News API key

# Categorized Keywords
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
        "India": [
            "ONGC", "IOC", "BPCL", "HPCL", "RIL", "Cairn"
        ],
        "Pakistan": [
            "OGDCL", "PPL", "MPCL", "PSO", "ARL", "Byco", "NRL",
            "PARCO", "SNGPL", "SSGC", "Hascol", "Pak LNG", "TOR"
        ],
        "Sri Lanka": [
            "Ceylon Petroleum Corporation", "Lanka IOC"
        ],
        "Bangladesh": [
            "Petrobangla", "BAPEX"
        ]
    }
}

# App Title
st.title("News Collector App")
st.subheader("Search for industry-specific news")

# User Input
selected_keywords = st.multiselect(
    "Select keywords to search news for:",
    options=[kw for cat in KEYWORDS.values() for kw in (cat if isinstance(cat, list) else [kw for r in cat.values() for kw in r])],
    default=["oil", "gas"]
)

selected_country = st.text_input(
    "Enter a country name (optional):", ""
)

# Fetch News Function
def fetch_news(keywords, country):
    query = " OR ".join(keywords)  # Combine keywords with OR for News API
    params = {
        "q": query,
        "language": "en",
        "apiKey": API_KEY,
        "sortBy": "relevancy"
    }
    response = requests.get(NEWS_API_URL, params=params)
    
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        if country:
            country = country.lower()
            articles = [
                article for article in articles
                if article.get("description") and country in article.get("description", "").lower()
            ]
        return articles
    else:
        return None

# Fetch and Display News
if st.button("Search News"):
    if not selected_keywords:
        st.error("Please select at least one keyword.")
    else:
        articles = fetch_news(selected_keywords, selected_country)
        if articles is not None:
            if articles:
                st.subheader("News Results:")
                for article in articles:
                    st.write(f"**{article['title']}**")
                    st.write(article['description'])
                    st.write(f"[Read more]({article['url']})")
                    st.write("---")
            else:
                st.warning("No articles found for the selected keywords.")
        else:
            st.error("Failed to fetch news. Please check your API key or try again later.")

# Sidebar for Keywords Reference
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

