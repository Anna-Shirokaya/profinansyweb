import os
import time
import urllib3
import requests
import pytest
from selenium import webdriver
from dotenv import load_dotenv
from api.accounts_api import AccountsAPI

import allure
from allure_commons.types import AttachmentType
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from pages.auth_pages.welcome_page import WelcomePage
from pages.auth_pages.login_page import LoginPage
from pages.dashboard_pages.dashboard_page import DashboardPage
from pages.debit_pages.accounts_main_page import AccountsMainPage
from api.accounts_api import AccountsAPI

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
        # Эти флаги жизненно важны для React-приложений в фоне
        options.add_argument("--blink-settings=imagesEnabled=true")
        options.add_argument("--force-device-scale-factor=1")
        
    browser = webdriver.Chrome(options=options)
    browser.set_window_size(1920, 1080)
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
    """Авторизация через API с сохранением JWT-токена и умным фоллбэком на UI-логин через PageObjects"""
    print("\n[DEBUG AUTH] --- СТАРТ АВТОРИЗАЦИИ ---")

    email = os.getenv("PROFINANSY_USER_EMAIL")
    password = os.getenv("PROFINANSY_USER_PASSWORD")
    if not email or not password:
        raise ValueError("[DEBUG AUTH] ОШИБКА: Учетные данные не найдены в .env!")

    base_url = driver.base_url.rstrip("/")
    is_qa = "qa.profinansy.dev" in base_url
    api_base_url = "https://qa.profinansy.dev" if is_qa else base_url

    session = requests.Session()
    session.verify = False

    # 1. ЖЕСТКАЯ ОЧИСТКА кук
    driver.delete_all_cookies()
    session.cookies.clear()

    common_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36",
        "Origin": base_url,
        "Referer": f"{base_url}/",
        "Accept": "application/json, text/plain, */*",
    }

    # Открываем базовый URL для генерации гостевой сессии браузером
    driver.get(base_url)
    time.sleep(2)
    
    # Синхронизируем куки браузера с сессией requests
    for cookie in driver.get_cookies():
        session.cookies.set(cookie["name"], cookie["value"])

    # 2. API Логин
    login_url = f"{api_base_url}/api/auth/login"
    login_headers = common_headers.copy()
    login_headers["Content-Type"] = "application/json"
    
    payload = {"acc_type": "email", "login": email, "pass": password, "web": True}
    
    print(f"[DEBUG AUTH] Отправляем POST запрос на логин: {login_url}")
    res_login = session.post(login_url, json=payload, headers=login_headers)
    
    if res_login.status_code != 200:
        print(f"[DEBUG AUTH] ОШИБКА БЭКЕНДА: {res_login.text}")
    res_login.raise_for_status()

    login_data = res_login.json()
    auth_token = login_data.get("token") or login_data.get("data", {}).get("token")
    
    if not auth_token:
        raise ValueError("[DEBUG AUTH] ОШИБКА: Токен не найден в ответе бэкенда!")
        
    # Обязательно сохраняем токен для создания счетов через API-фикстуру
    driver.api_auth_token = auth_token
    print(f"[DEBUG AUTH] Боевой токен успешно получен! Длина: {len(auth_token)}")

    # 3. Инъекция токена в localStorage
    domain_name = ".profinansy.dev" if is_qa else ".profinansy.ru"
    for cookie in session.cookies:
        try:
            driver.add_cookie({"name": cookie.name, "value": cookie.value, "path": "/", "domain": domain_name})
        except Exception:
            pass

    try:
        driver.execute_script(f"window.localStorage.setItem('token', '{auth_token}');")
        driver.execute_script("window.localStorage.setItem('isAuth', 'true');")
    except Exception as e:
        print(f"[DEBUG AUTH] Ошибка localStorage: {e}")

    # 4. Переход в кошелек
    target_url = f"{base_url}/wallet/accounts"
    driver.get(target_url)
    time.sleep(3) 
    
    # 5. ПРОВЕРКА РЕДИРЕКТА И UI-ФОЛЛБЭК
    current_url = driver.current_url
    if "login" in current_url or "welcome" in current_url:
        print("[DEBUG AUTH] Обнаружен редирект на логин! Выполняем UI-авторизацию через PageObjects...")
        
        welcome_page = WelcomePage(driver)
        login_page = LoginPage(driver)
        dashboard_page = DashboardPage(driver)
        
        # Если нас кинуло на приветственную страницу, нажимаем "Войти"
        if "welcome" in current_url:
            welcome_page.click_login_button()
            
        # Заполняем форму через ваши готовые методы
        login_page.enter_email(email)
        login_page.enter_password(password)
        login_page.click_submit_button()

        # Даем странице время загрузить дашборд и выкинуть первые баннеры
        time.sleep(4) 
        
        # --- БОРЬБА С МНОЖЕСТВЕННЫМИ БАННЕРАМИ НА ПРОДЕ ---
        accounts_page_for_promo = AccountsMainPage(driver)
        for _ in range(4):  # Пробуем закрыть до 3 баннеров подряд
            try:
                accounts_page_for_promo.close_promo_popup_if_present()
                time.sleep(1.5)  # Ждем, вдруг после закрытия вылезет следующий
            except Exception:
                pass
        # --------------------------------------------------
        
        # Ждем успешного входа
        is_header_visible = dashboard_page.is_my_money_header_visible()
        if not is_header_visible:
            raise RuntimeError("[DEBUG AUTH] UI-авторизация не удалась (заголовок не найден)!")
            
        print("[DEBUG AUTH] UI-авторизация прошла успешно!")
        
        # Возвращаемся в кошелек, если после логина оказались не там
        if "/wallet/accounts" not in driver.current_url:
            driver.get(target_url)
            time.sleep(3)
    else:
        print("[DEBUG AUTH] --- АВТОРИЗАЦИЯ УСПЕШНА (Инъекция сработала) ---")
        
    yield driver


@pytest.fixture
def accounts_api(api_logged_in_driver):
    """Фикстура для API счетов. Использует 100% валидный токен из фикстуры авторизации"""
    driver = api_logged_in_driver
    
    # Забираем токен, который мы заботливо сохранили при логине
    token = getattr(driver, "api_auth_token", None)
    
    if not token:
        raise ValueError("[DEBUG API SETUP] КРИТИЧЕСКАЯ ОШИБКА: Боевой токен не был получен при логине!")
        
    return AccountsAPI(base_url=driver.base_url, token=token)

@pytest.fixture(scope="function")
def account_cleanup_registry(driver):
    """Единая фикстура для регистрации и автоматического удаления созданных счетов"""
    created_accounts = []
    
    yield created_accounts  
    
    if created_accounts and "/login" not in driver.current_url:
        print("\n[TEARDOWN] Начинаем автоматическую очистку...")
        dashboard_page = DashboardPage(driver)
        accounts_page = AccountsMainPage(driver)
        
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
def api_account_cleanup_registry(accounts_api):
    """Универсальный реестр очистки счетов через API.
    Поддерживает банковские счета, накопительные счета и портфели.
    """
    registry = []
    
    yield registry

    print("\n[TEARDOWN API] Начинаем автоматическую очистку через API...")
    for item in registry:
        try:
            if isinstance(item, tuple):
                acc_type, acc_id = item
                if acc_type in ["bank", "debit", "credit"]:
                    accounts_api.delete_account(acc_id)
                elif acc_type in ["savings", "accumulation"]:
                    accounts_api.delete_accumulation_account(acc_id)
                elif acc_type in ["portfolio", "investment", "invest"]:
                    accounts_api.delete_investment_account(acc_id)
                else:
                    accounts_api.delete_account(acc_id)
            else:
                # По умолчанию считаем обычным банковским счетом
                accounts_api.delete_account(item)
        except Exception as e:
            print(f"[TEARDOWN API] Ошибка при удалении {item}: {e}")


