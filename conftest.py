import os
import requests  # Добавлен недостающий импорт для API-авторизации
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

load_dotenv()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Фиксирует статус выполнения этапов теста (setup, call) в объекте item"""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture(
    params=[
        "https://profinansy.ru", 
        "https://frontend.qa.profinansy.dev"
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
    
    # --- TEARDOWN: Скриншот и DOM при любой ошибке ---
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
            print("[TEARDOWN] Скриншот и HTML ошибки успешно прикреплены к Allure.")
        except Exception as e:
            print(f"[TEARDOWN ERROR] Не удалось сохранить артефакты: {e}")

    print(f"\n[TEARDOWN] Закрытие браузера для {current_domain}...")
    browser.quit()


@pytest.fixture
def logged_in_driver(driver):
    print("\n[AUTH SETUP] Начало автоматической авторизации...")

    login_page = LoginPage(driver)
    dashboard_page = DashboardPage(driver)
    accounts_page = AccountsMainPage(driver)

    email = os.getenv("PROFINANSY_USER_EMAIL")
    password = os.getenv("PROFINANSY_USER_PASSWORD")
    
    if not email or not password:
        raise ValueError("[AUTH ERROR] Не найдены переменные окружения EMAIL или PASSWORD!")

    login_page.open()

    login_page.enter_email(email)
    login_page.enter_password(password)
    login_page.click_submit_button()

    WebDriverWait(driver, 15).until_not(
        EC.url_contains("/login")
    )

    dashboard_page.close_popup_if_exists()
    accounts_page.close_promo_popup_if_present()

    WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located(dashboard_page.MY_MONEY_HEADER)
    )

    print("[AUTH SETUP] Авторизация успешно завершена.")
    yield driver


@pytest.fixture(scope="function")
def account_cleanup_registry(logged_in_driver):
    """Единая фикстура для регистрации и автоматического удаления созданных счетов"""
    created_accounts = []
    
    yield created_accounts  
    
    if created_accounts and "/login" not in logged_in_driver.current_url:
        print("\n[TEARDOWN] Начинаем автоматическую очистку...")
        dashboard_page = DashboardPage(logged_in_driver)
        accounts_page = AccountsMainPage(logged_in_driver)
        
        try:
            if not accounts_page.is_page_loaded():
                dashboard_page.open_accounts_section()
                
            for account_name in created_accounts:
                with allure.step(f"[TEARDOWN] Очистка: удаление счета '{account_name}'"):
                    accounts_page.close_promo_popup_if_present()
                    
                    print(f"[TEARDOWN] Удаляем счет: '{account_name}'")
                    accounts_page.click_three_dots_for_account(account_name)
                    accounts_page.click_delete_account_in_dropdown()
                    accounts_page.click_confirm_delete_first_stage()
                    accounts_page.tick_both_delete_checkboxes()
                    accounts_page.click_confirm_delete_final_stage()
                    print(f"[TEARDOWN] Счет '{account_name}' успешно удален.")
                    
        except Exception as e:
            print(f"[TEARDOWN] Предупреждение: Не удалось очистить счета. Ошибка: {e}")


@pytest.fixture
def api_logged_in_driver(driver):
    """Быстрая авторизация через API без прохождения UI-шагов входа"""
    print("\n[AUTH API] Запуск авто-авторизации через API...")

    email = os.getenv("PROFINANSY_USER_EMAIL")
    password = os.getenv("PROFINANSY_USER_PASSWORD")

    if not email or not password:
        raise ValueError("[AUTH API ERROR] Переменные PROFINANSY_USER_EMAIL или PROFINANSY_USER_PASSWORD не найдены!")

    base_url = driver.base_url
    session = requests.Session()

    session_url = f"{base_url}/api/auth/session?type=web"
    res_session = session.get(session_url)
    res_session.raise_for_status()
    
    session_data = res_session.json()
    anon_token = session_data.get("token") or session_data.get("data", {}).get("token")
    
    if not anon_token:
        raise ValueError(f"[AUTH API ERROR] Не удалось извлечь токен из ответа: {session_data}")

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