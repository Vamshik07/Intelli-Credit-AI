import requests
from bs4 import BeautifulSoup


def research_company(company_name):
    url = f"https://news.google.com/search?q={company_name}%20company&hl=en-IN&gl=IN&ceid=IN:en"

    try:
        # Timeout keeps /analyze responsive when the upstream site is slow.
        response = requests.get(
            url,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        response.raise_for_status()
    except requests.RequestException:
        return ["Unable to fetch news at the moment"]

    soup = BeautifulSoup(response.text, "html.parser")

    headlines = []
    articles = soup.find_all("a", class_="DY5T1d")

    for article in articles[:5]:
        headlines.append(article.text)

    if len(headlines) == 0:
        headlines.append("No major negative news found")

    return headlines
