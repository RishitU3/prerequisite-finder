# ==============================================================================
# File: src/scrapers/scraper.py (Updated)
#
# This script is a more advanced web crawler, now more robust and less
# sensitive to website-specific formatting. It is designed to find and
# scrape prerequisite data from a predefined set of academic websites.
#
# Changes:
# - Broader keyword search for course links to find more pages.
# - Improved course title and prerequisite extraction logic for better accuracy.
# - Refined crawling logic to correctly identify and scrape more courses.
# ==============================================================================

import requests
from bs4 import BeautifulSoup
import json
import os
import re
from urllib.parse import urljoin, urlparse
from collections import deque

# Define the root directory for the data.
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Define the path for the output JSON file.
OUTPUT_FILE = os.path.join(DATA_DIR, "prereqs.json")

# A list of starting URLs for the crawler, focused on specified sources.
STARTING_URLS = [
    "https://ocw.mit.edu/courses/find-by-topic/#cat=engineering&subcat=computer-science",
    "https://ocw.mit.edu/courses/find-by-topic/#cat=science&subcat=mathematics",
    "https://onlinecourses.swayam2.ac.in/course_category_list",
    "https://www.bmsce.ac.in/department/computer-science-and-engineering/course-curriculum",
]

# A more comprehensive list of keywords to identify course-related links.
# This list is now more general to match a wider variety of URL structures.
COURSE_LINK_KEYWORDS = [
    r'courses/',
    r'subjects/',
    r'syllabus/',
    r'curriculum/',
    r'program/',
    r'academic/',
    r'course-detail/',
    r'\d{2,4}[a-z]?-',  # A pattern for course codes like "6-006" or "CS-101"
]


def get_html(url):
    """
    Fetches the HTML content from a given URL with error handling.

    Args:
        url (str): The URL to fetch.

    Returns:
        str: The HTML content as a string, or None on failure.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def find_course_links(html, base_url):
    """
    Finds all potential course links in the given HTML.

    Args:
        html (str): The HTML content to parse.
        base_url (str): The base URL of the page being crawled.

    Returns:
        set: A set of absolute URLs that are potential course links.
    """
    soup = BeautifulSoup(html, 'html.parser')
    links = set()
    for link in soup.find_all('a', href=True):
        href = link['href']
        absolute_url = urljoin(base_url, href)

        # Use case-insensitive search to check if the link is relevant
        if any(re.search(keyword, absolute_url, re.IGNORECASE) for keyword in COURSE_LINK_KEYWORDS):
            # Check if the link contains a common course code pattern to confirm it's a course page
            if re.search(r'\d{2,4}[a-z]?', absolute_url, re.IGNORECASE):
                links.add(absolute_url)
            # Add general links that might lead to a course page
            elif not re.search(r'#|javascript|mailto', absolute_url, re.IGNORECASE):
                links.add(absolute_url)
    return links


def scrape_prerequisites(url):
    """
    Scrapes a single URL for course title and prerequisites.

    Args:
        url (str): The URL of the course page.

    Returns:
        dict: A dictionary containing the course title, prerequisites, and source,
              or None if the data could not be found.
    """
    html = get_html(url)
    if not html:
        return None

    soup = BeautifulSoup(html, 'html.parser')

    # --- Prerequisite Extraction Logic ---
    prereq_text = None
    # Find a heading or strong tag containing "prerequisite" (case-insensitive)
    prereq_heading = soup.find(
        lambda tag: tag.name in ['h2', 'h3', 'h4', 'strong'] and ('prerequisite' in tag.get_text().lower()))
    if prereq_heading:
        next_element = prereq_heading.find_next_sibling(['p', 'ul', 'div'])
        if next_element:
            prereq_text = next_element.get_text(separator=' ', strip=True)

    # Fallback: Search the entire body text if no specific heading is found
    if not prereq_text:
        body_text = soup.get_text()
        prereq_match = re.search(r'prerequisite[s]?:?\s*(.*)', body_text, re.IGNORECASE)
        if prereq_match:
            # Take the first sentence after the match
            prereq_text = prereq_match.group(1).split('.')[0].strip()

    # --- Course Title Extraction Logic ---
    course_title_tag = soup.find(['h1', 'h2', 'h3']) or soup.find('title')
    if course_title_tag:
        course_title = course_title_tag.get_text().strip()
    else:
        # Fallback to URL path if no title tag is found
        course_title = url.split('/')[-1].replace('-', ' ').replace('_', ' ').strip()

    if prereq_text:
        # Extract course codes from the prerequisite text
        course_codes = re.findall(r'[A-Z]{2,4}\s?\d{2,4}[A-Z]?', prereq_text, re.IGNORECASE)
        prereqs = ', '.join(course_codes) if course_codes else prereq_text
    else:
        prereqs = "Not specified"

    return {
        "title": course_title,
        "prerequisites": prereqs,
        "source": url
    }


def main():
    """
    Main function to orchestrate the scraping and crawling process.
    """
    all_prereqs = []

    # Use a queue for a breadth-first search (BFS) crawling approach
    queue = deque(STARTING_URLS)
    visited_urls = set(STARTING_URLS)
    course_urls_to_scrape = set()

    print("Starting to crawl for course links...")

    while queue:
        current_url = queue.popleft()
        print(f"Crawling: {current_url}")

        html = get_html(current_url)
        if html:
            found_links = find_course_links(html, current_url)
            for link in found_links:
                if link not in visited_urls:
                    visited_urls.add(link)
                    # Limit the crawl to a single domain to avoid going off-site
                    if urlparse(link).netloc == urlparse(current_url).netloc:
                        queue.append(link)

                    # Add links that look like a specific course page to the scraping list
                    if re.search(r'\d{2,4}[a-z]?', link, re.IGNORECASE):
                        course_urls_to_scrape.add(link)

    print(f"\nFound {len(course_urls_to_scrape)} potential course pages. Starting to scrape...")

    # Now, scrape the unique course pages we've found
    for url in course_urls_to_scrape:
        print(f"Scraping: {url}")
        data = scrape_prerequisites(url)
        if data and data.get("title") and data["prerequisites"] != "Not specified":
            all_prereqs.append(data)
            print(f"  - Found: '{data['title']}' with prerequisites: {data['prereqs']}")
        else:
            print("  - No relevant data found or an error occurred.")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_prereqs, f, indent=4)

    print("\nScraping complete!")
    print(f"Data saved to {OUTPUT_FILE}")
    print(f"Total courses with prerequisites found: {len(all_prereqs)}")


if __name__ == "__main__":
    main()

