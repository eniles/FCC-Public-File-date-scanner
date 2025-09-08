import requests
from bs4 import BeautifulSoup

# URL of the FCC Public File site (example)
URL = "https://publicfiles.fcc.gov/am-profile/"

response = requests.get(URL)
soup = BeautifulSoup(response.text, "html.parser")

for link in soup.find_all("a"):
    href = link.get("href")
    if href and "publicfile" in href:
        print(href)
        # Attempt to print document date if available in link text
        print(link.text.strip())