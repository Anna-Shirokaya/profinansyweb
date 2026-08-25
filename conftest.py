import os
import urllib3
import requests
import pytest
from selenium import webdriver
from dotenv import load_dotenv

import allure
from allure_commons.types import AttachmentType

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.auth_pages.welcome_page import WelcomePage
from pages.auth_pages.login_page import LoginPage
from pages.dashboard_pages.dashboard_page import DashboardPage
from pages.debit_pages.accounts_main_page import AccountsMainPage

# Отключаем предупреждения urllib3 о незащищенных SSL-запросах (verify=False)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture(
    params=[
        "https://profinansy.ru", 
        "https://frontend.qa.profinansy.dev"  # Точный URL QA-стенда
    ], 
    scope="function"
)
def driver(request):
    current_domain = request.param
    print(f"\n[SETUP] Запуск браузера для окружения: {current_domain}")
    
    options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications": 2}
    options.add_experimental_option("prefs", prefs)
    
    options.page_load_strategy = 'normal'
    
    # Флаги для обхода проблем с SSL и сетью на DEV-стендах
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--acceptInsecureCerts")
    
    options.add_argument("--window-size=1920,1080") 
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-renderer-backgrounding")
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--log-level=3")
    options.add_argument("--silent")
    options.add_argument("--mute-audio")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    if os.getenv("CI") == "true":
        print("[SETUP] Обнаружена CI-среда. Запуск в фоновом (headless) режиме...")
        options.add_argument("--headless=new")
        
    browser = webdriver.Chrome(options=options)
    browser.base_url = current_domain
    
    yield browser
    
    rep_call = getattr(request.node, "rep_call", None)
    rep_setup = getattr(request.node, "rep_setup", None)

    if (rep_call and rep_call.failed) or (rep_setup and rep_setup.failed):
        try:
            allure.attach(
                browser.get_screenshot_as_png(),
                name="failure_screenshot",
                attachment_type=AttachmentType.PNG
            )
            allure.attach(
                browser.page_source,
                name="failure_page_source",
                attachment_type=AttachmentType.HTML
            )
        except Exception as e:
            print(f"[TEARDOWN ERROR] Не удалось сохранить артефакты: {e}")

    print(f"\n[TEARDOWN] Закрытие браузера для {current_domain}...")
    browser.quit()


@pytest.fixture
def api_logged_in_driver(driver):
    """Авторизация через API с отключенной проверкой SSL-сертификата"""
    print("\n[AUTH API] Запуск авто-авторизации через API...")

    email = os.getenv("PROFINANSY_USER_EMAIL")
    password = os.getenv("PROFINANSY_USER_PASSWORD")

    if not email or not password:
        raise ValueError("[AUTH API ERROR] Переменные PROFINANSY_USER_EMAIL или PROFINANSY_USER_PASSWORD не найдены!")

    base_url = driver.base_url
    session = requests.Session()
    session.verify = False  # Отключаем строгую проверку SSL для запросов к QA

    session_url = f"{base_url}/api/auth/session?type=web"
    res_session = session.get(session_url)
    res_session.raise_for_status()
    
    session_data = res_session.json()
    anon_token = session_data.get("token") or session_data.get("data", {}).get("token")
    
    login_url = f"{base_url}/api/auth/login"
    headers = {
        "token": anon_token,
        "Content-Type": "application/json"
    }
    payload = {
        "acc_type": "email",
        "login": email,
        "pass": password,
        "web": True
    }

    res_login = session.post(login_url, json=payload, headers=headers)
    res_login.raise_for_status()
    
    login_data = res_login.json()
    auth_token = login_data.get("token") or login_data.get("data", {}).get("token") or anon_token

    driver.get(base_url)

    driver.execute_script(f"window.localStorage.setItem('token', '{auth_token}');")
    driver.execute_script(f"window.localStorage.setItem('auth_token', '{auth_token}');")

    for cookie in session.cookies:
        try:
            driver.add_cookie({
                "name": cookie.name,
                "value": cookie.value,
                "path": cookie.path or "/",
            })
        except Exception:
            pass

    driver.refresh()

    dashboard_page = DashboardPage(driver)
    WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located(dashboard_page.MY_MONEY_HEADER)
    )

    print("[AUTH API] Успешная авторизация! Сессия прокинута в браузер.")
    yield driver