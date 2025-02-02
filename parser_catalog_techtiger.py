import time
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import json



headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
}

session = requests.Session()
session.cookies.update({'cookie_name': 'cookie_value'})
response = requests.get('https://techtiger.ru/catalog/', headers=headers)
url_for_json = 'https://techtiger.ru'
SAVE_DIR = 'data_json'
# JSON_FILE = "save_products.json"
options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # безголовый режим
driver = webdriver.Chrome(options=options)

def get_link():
    """ Получаем все категории и ссылки на них, сохраняем в json """
    list_of_products = {}

    soup = BeautifulSoup(response.text, 'html.parser')  # Используем BeautifulSoup для извлечения данных.
    products = soup.find_all('div', class_='item_block lg col-lg-20 col-md-4 col-xs-6')
    for link in products:
        category_url = link.find('a').get('href')
        category_name = link.text.strip('\n').split()[0].replace('/', '_')
        list_of_products[category_name] = url_for_json + category_url

    return list_of_products


def reed_json_list():
    """ Читаем товары по категориям из json """
    with open('list_of_products.json', "r", encoding="utf-8") as file:
        dict_from_json = json.load(file)
        for name_category, link_text in dict_from_json.items():
            print(f"Взял ссылку - {link_text}")
            scrol_to_end(name_category, link_text)
            time.sleep(10)


def scrol_to_end(name_category: str, link_category: str):
    """ Скроллинг страницы с помощью Selenium """
    scrl_count = 0
    driver.get(link_category)
    # driver.get('https://techtiger.ru/catalog/podveska/')
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)  # скролл до конца
        time.sleep(5)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("✅ Достигнут конец страницы.")
            break
        last_height = new_height
        scrl_count += 1
        print(f'скроллим дальше')

        save_products(driver, name_category)

    print(f'Всего скроллов = {scrl_count}')


def save_products(driver, name_category: str):
    """ Собирает товары и дописывает их в JSON-файл """
    # JSON_FILE = "save_products.json"
    JSON_FILE = os.path.join(SAVE_DIR, f"{name_category}_save_products.json")
    page_source = driver.page_source  # получаем актуальную страницу для парсинга после прокрутки
    soup = BeautifulSoup(page_source, 'html.parser')
    products = soup.find_all('div', class_='item_info')
    # Загружаем уже сохраненные товары
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as file:
            find_list_json = json.load(file)
            print('открыл файл')
    except (FileNotFoundError, json.JSONDecodeError):
        find_list_json = []  # Если файла нет, создаём новый словарь
        print("Файл не найден, создаём новый.")

    print(f"📂 Текущие товары в JSON перед проверкой: {len(find_list_json)}")
    for product in products:
        product_url = url_for_json + product.find('a').get('href')

        product_name_tag = product.find('div', class_='item-title')
        product_name = product_name_tag.text.strip() if product_name_tag else "Без названия"

        price_tag = product.find('div', class_='price font-bold font_mxs')
        price = price_tag['data-value'] if price_tag and 'data-value' in price_tag.attrs else "Нет цены"

        # Проверяем, есть ли товар в списке (по имени)
        if not any(item["name"] == product_name for item in find_list_json):
            find_list_json.append({"name": product_name, "price": price, "url": product_url})
            # print(f"✅ Добавлено: {product_name} - {price} руб.")

        # Записываем обновленные данные в файл
    with open(JSON_FILE, "w", encoding="utf-8") as file:
        json.dump(find_list_json, file, indent=4, ensure_ascii=False)

    print(f"Товары сохранены в {JSON_FILE}")

# get_link()

# list_of_products = get_link()
# with open('list_of_products.json', "w", encoding="utf-8") as file:
#     json.dump(list_of_products, file, indent=4, ensure_ascii=False)
# print("✅ Категории сохранены в categories.json")

reed_json_list()
driver.quit()




