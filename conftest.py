import os
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

@pytest.fixture(params=["https://profinansy.ru"], scope="function")
def driver(request):
    current_domain = request.param
    print(f"\n[SETUP] Запуск браузера для окружения: {current_domain}")
    
    options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications": 2}
    options.add_experimental_option("prefs", prefs)
    
    # 1. Возвращаем нормальную стратегию загрузки ('normal' вместо 'eager')
    options.page_load_strategy = 'normal'
    
    # Базовые флаги для стабильности
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

    # 2. Убираем дублирование: headless включается ТОЛЬКО на CI
    if os.getenv("CI") == "true":
        print("[SETUP] Обнаружена CI-среда. Запуск в фоновом (headless) режиме...")
        options.add_argument("--headless=new")
        
    browser = webdriver.Chrome(options=options)
    browser.base_url = current_domain
    
    yield browser
    
    print(f"\n[TEARDOWN] Закрытие браузера для {current_domain}...")
    browser.quit()

@pytest.fixture
def logged_in_driver(driver):
    print("\n[AUTH SETUP] Начало автоматической авторизации...")

    login_page = LoginPage(driver)
    dashboard_page = DashboardPage(driver)

    email = os.getenv("PROFINANSY_USER_EMAIL")
    password = os.getenv("PROFINANSY_USER_PASSWORD")
    
    if not email or not password:
        raise ValueError("[AUTH ERROR] Не найдены переменные окружения EMAIL или PASSWORD!")

    login_page.open()

    # 3. Ввод данных с неявным ожиданием готовности формы
    login_page.enter_email(email)
    login_page.enter_password(password)
    login_page.click_submit_button()

    WebDriverWait(driver, 15).until_not(
        EC.url_contains("/login")
    )

    dashboard_page.close_popup_if_exists()

    WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located(dashboard_page.MY_MONEY_HEADER)
    )

    print("[AUTH SETUP] Авторизация успешно завершена.")
    yield driver

@pytest.fixture(scope="function")
def account_cleanup_registry(logged_in_driver):
    accounts_to_delete = []
    yield accounts_to_delete
    
    if accounts_to_delete and "/login" not in logged_in_driver.current_url:
        print("\n[TEARDOWN] Начинаем автоматическую очистку...")
        dashboard_page = DashboardPage(logged_in_driver)
        accounts_page = AccountsMainPage(logged_in_driver)
        
        try:
            if not accounts_page.is_page_loaded():
                dashboard_page.open_accounts_section()
                
            for account_name in accounts_to_delete:
                # 📍 Закрываем любые промо-окна ПЕРЕД попыткой взаимодействия с карточкой
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


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    
    # Если ошибка произошла на этапе setup или call
    if rep.when in ("setup", "call") and rep.failed:
        driver = item.funcargs.get("driver") or item.funcargs.get("logged_in_driver")
        if driver:
            # Делаем скриншот
            allure.attach(
                driver.get_screenshot_as_png(),
                name=f"screenshot_{rep.when}_failure",
                attachment_type=AttachmentType.PNG
            )
            # Сохраняем HTML-код страницы
            allure.attach(
                driver.page_source,
                name=f"page_source_{rep.when}_failure",
                attachment_type=AttachmentType.HTML
            )


@pytest.fixture
def account_cleanup_registry(logged_in_driver):
    created_accounts = []
    
    # 1. Передаем реестр в тест
    yield created_accounts  
    
    # 2. TEARDOWN: Выполняется ПОСЛЕ завершения теста (даже при упавших assert!)
    if created_accounts:
        accounts_page = AccountsMainPage(logged_in_driver)
        for account_name in created_accounts:
            with allure.step(f"[TEARDOWN] Очистка: удаление счета '{account_name}'"):
                try:
                    print(f"\n[TEARDOWN] Удаляем счет: '{account_name}'")
                    accounts_page.click_three_dots_for_account(account_name)
                    accounts_page.click_delete_account_in_dropdown()
                    accounts_page.click_confirm_delete_first_stage()
                    accounts_page.tick_both_delete_checkboxes()
                    accounts_page.click_confirm_delete_final_stage()
                    print(f"[TEARDOWN] Счет '{account_name}' успешно удален.")
                except Exception as e:
                    print(f"[TEARDOWN] Предупреждение: не удалось удалить счет '{account_name}'. Ошибка: {e}")

@pytest.fixture(autouse=True)
def clear_popups_before_test(logged_in_driver):
    """Автоматически проверяет и закрывает случайные баннеры перед началом каждого теста"""
    from pages.debit_pages.accounts_main_page import AccountsMainPage
    
    try:
        # Инициализируем страницу и закрываем баннер, если он уже на экране
        accounts_page = AccountsMainPage(logged_in_driver)
        accounts_page.close_promo_popup_if_present()
    except Exception as e:
        print(f"[FIXTURE AUTO] Не удалось выполнить предпроверку баннеров: {e}")
        
    yield