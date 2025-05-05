import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import quote
import random

# основной запрос
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/103.0.0.0 Safari/537.36"
    )
}

# запасные варианты на самый крайний случай
FALLBACK_DISHES = [
    "борщтч",
    "жаренные пельмени",
    "уху",
    "оливьешку",
    "блинчики",
    "шашлычок",
    "вареники",
    "солянку",
    "пирожки",
    "окрошку"
]


def get_country_cuisine_url(country_name):
    # начинает делаться запросик
    base_url = "https://en.wikipedia.org/wiki/Cuisine_of_"
    country_formatted = country_name.strip().replace(' ', '_')
    return base_url + country_formatted


def fetch_page(url):
    # продолжается делаться запросик
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching page {url}: {e}")
        return None


def parse_dishes_sections(html, max_items=5):
    # фильтрация хтмл и нахождение из хтмл блюда и тому пдобное
    soup = BeautifulSoup(html, 'html.parser')
    content = soup.find(id='mw-content-text')
    if not content:
        return []

    items = []
    relevant_sections = [
        "dish",
        "food",
        "cuisine",
        "meal",
        "recipe",
        "specialty",
        "appetizer",
        "dessert",
        "snack"
    ]

    for header in content.find_all(['h2', 'h3', 'h4']):
        heading_text = header.get_text(separator=" ", strip=True)
        heading_text_clean = re.sub(r'\[edit\]', '', heading_text, flags=re.I).lower()

        if any(keyword in heading_text_clean for keyword in relevant_sections):
            for sibling in header.find_next_siblings():
                if sibling.name and sibling.name.startswith('h') and len(sibling.name) <= len(header.name):
                    break
                if sibling.name == 'ul':
                    for li in sibling.find_all('li', recursive=False):
                        text = li.get_text(separator=' ', strip=True)
                        text = re.sub(r'\[\d+\]', '', text)
                        word_count = len(text.split())
                        if 1 <= word_count <= 7:
                            items.append(text)
                if len(items) >= max_items * 2:
                    break
            if len(items) >= max_items * 2:
                break

    unique_items = []
    for item in items:
        if item not in unique_items:
            unique_items.append(item)
        if len(unique_items) >= max_items:
            break
    return unique_items


def parse_general_dishes(html, max_items=5):
    # ассматривается хтмл запрос и ищутся нужные вещи
    soup = BeautifulSoup(html, 'html.parser')
    items = []

    for ul in soup.find_all('ul'):
        for li in ul.find_all('li', recursive=False):
            text = li.get_text(separator=' ', strip=True)
            text = re.sub(r'\[\d+\]', '', text)
            word_count = len(text.split())
            if 1 <= word_count <= 7:
                items.append(text)
        if len(items) >= max_items * 3:
            break

    unique_items = []
    for item in items:
        if item not in unique_items:
            unique_items.append(item)
        if len(unique_items) >= max_items:
            break
    return unique_items


def google_search_urls(query, max_results=5):
    # делается запрос в гугл и смотрятся разные вещи
    search_url = f"https://www.google.com/search?q={quote(query)}&hl=en"
    try:
        resp = requests.get(search_url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')

        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith("/url?q="):
                url = href.split("/url?q=")[1].split("&")[0]
                if url and (url not in links):
                    links.append(url)
                if len(links) >= max_results:
                    break
        return links
    except requests.RequestException as e:
        return []


def get_dishes_from_search_queries(country_name, max_dishes=5):
    dishes = []
    queries = [f"food {country_name}", f"{country_name} food"]

    for query in queries:
        urls = google_search_urls(query, max_results=3)
        for url in urls:
            html = fetch_page(url)
            if not html:
                continue
            found_items = parse_general_dishes(html, max_items=max_dishes)
            for item in found_items:
                if item not in dishes:
                    dishes.append(item)
                    if len(dishes) >= max_dishes:
                        return dishes
    return dishes


def fallback_no_dishes_message(country):
    dish = random.choice(FALLBACK_DISHES)
    print(f"Из {country} нет ничего интересного, лучше поешь {dish}")


def get_dishes_by_country(country_name):
    # Попытка 1: поиск еды из страны
    url = get_country_cuisine_url(country_name)
    html = fetch_page(url)
    if html:
        dishes = parse_dishes_sections(html, max_items=5)
        if dishes:
            return dishes
    # Попытка 2: если ничего не найдено, то пробовать найти еду из викепедии
    fallback_url = "https://en.wikipedia.org/wiki/Dish"
    fallback_html = fetch_page(fallback_url)
    if fallback_html:
        fallback_dishes = parse_dishes_sections(fallback_html, max_items=10)
        if fallback_dishes:
            return fallback_dishes
    # Попытка 3: если ничего не найдено в предыдущих запросах, поиск в поисковых системах
    search_dishes = get_dishes_from_search_queries(country_name, max_dishes=5)
    if search_dishes:
        return search_dishes
    # Финальная попытка: если каким-то чудом из всех предыдущих запросов ничего не найдено, то делается это
    fallback_no_dishes_message(country_name)
    return []


async def food_seach(update, context):
    country = context.user_data["country"]
    dishes = get_dishes_by_country(country)
    if dishes:
        await update.message.reply_text(f"Блюда из {country}:")
        for i, dish in enumerate(dishes, 1):
            await update.message.reply_text(f"{i}. {dish}")
