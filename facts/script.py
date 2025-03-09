import requests
from bs4 import BeautifulSoup
import csv

# List of category URLs to scrape
CATEGORY_URLS = [
    "https://faktid.ee/category/ajalugu/",
    "https://faktid.ee/category/faktid-autode-kohta/",
    "https://faktid.ee/category/faktid-eesti-kohta/",
    "https://faktid.ee/category/foobiad/",
    "https://faktid.ee/category/faktid-inimeste-kohta/",
    "https://faktid.ee/category/kosmos/",
    "https://faktid.ee/category/kuulsused/",
    "https://faktid.ee/category/faktid-loomade-kohta/",
    "https://faktid.ee/category/maailm/",
    "https://faktid.ee/category/faktid-meeste-kohta/"
]

# Output file
OUTPUT_FILE = "../all_facts.csv"

def scrape_facts():
    all_facts = []

    for category_url in CATEGORY_URLS:
        category_name = category_url.split("/")[-2]  # Extract category name from URL
        page_number = 1

        while True:
            url = f"{category_url}page/{page_number}/"
            print(f"Scraping {category_name}, page {page_number}: {url}")

            response = requests.get(url)
            if response.status_code != 200:
                print(f"Stopped at {category_name}, page {page_number}. No more pages found.")
                break

            soup = BeautifulSoup(response.text, "html.parser")

            # Find all h1 tags with class 'entry-title'
            fact_elements = soup.find_all("h1", class_="entry-title")

            if not fact_elements:
                print(f"No more facts found for {category_name}. Moving to next category.")
                break

            # Extract text and store in list
            for element in fact_elements:
                fact = element.get_text(strip=True)
                all_facts.append([category_name, fact])  # Store category name along with the fact

            page_number += 1

    # Save facts to CSV
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Category", "Fact"])  # Write header
        writer.writerows(all_facts)  # Write facts

    print(f"Scraping completed. {len(all_facts)} facts saved to {OUTPUT_FILE}.")

if __name__ == "__main__":
    scrape_facts()
