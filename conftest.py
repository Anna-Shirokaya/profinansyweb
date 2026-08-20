import os
import pytest
from selenium import webdriver
from dotenv import load_dotenv

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.auth_pages.welcome_page import WelcomePage
from pages.auth_pages.login_page import LoginPage
from pages.dashboard_pages.dashboard_page import DashboardPage
from pages.debit_pages.accounts_main_page import AccountsMainPage

load_dotenv()

# Добавляем параметризацию: перечисляем твои домены в params
#@pytest.fixture(params=["https://profinansy.ru", "https://qa.profinansy.dev"], scope="function")
@pytest.fixture(params=["https://profinansy.ru"], scope="function")
def driver(request):
    """Базовая фикстура: запускает браузер и прикрепляет к нему текущий домен"""
    current_domain = request.param
    print(f"\n[SETUP] Запуск браузера для окружения: {current_domain}")
    
    options = webdriver.ChromeOptions()
    # Блокируем системное окно "profinansy.ru wants to Show notifications"
    prefs = {"profile.default_content_setting_values.notifications": 2}
    options.add_experimental_option("prefs", prefs)
    options.page_load_strategy = 'eager'
    options.add_argument("--window-size=1920,1080") 
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-renderer-backgrounding")
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--log-level=3")
    options.add_argument("--silent")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--mute-audio")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    # Включаем headless ТОЛЬКО на CI-сервере (GitHub Actions и т.д.)
    if os.getenv("CI") == "true":
        print("[SETUP] Обнаружена CI-среда. Запуск в фоновом (headless) режиме...")
        options.add_argument("--headless=new")
        
    browser = webdriver.Chrome(options=options)
    
    #записываем текущий домен прямо внутрь объекта browser.
    browser.base_url = current_domain
    
    yield browser
    
    print(f"\n[TEARDOWN] Закрытие браузера для {current_domain}...")
    browser.quit()

@pytest.fixture
def logged_in_driver(driver):
    """Фикстура авторизации: переход напрямую на страницу входа"""
    print("\n[AUTH SETUP] Начало автоматической авторизации...")

    login_page = LoginPage(driver)
    dashboard_page = DashboardPage(driver)

    email = os.getenv("PROFINANSY_USER_EMAIL")
    password = os.getenv("PROFINANSY_USER_PASSWORD")
    
    if not email or not password:
        raise ValueError("[AUTH ERROR] Не найдены переменные окружения EMAIL или PASSWORD!")

    # 1. Переходим сразу на страницу входа
    login_page.open()

    # 2. Вводим данные и отправляем форму
    login_page.enter_email(email)
    login_page.enter_password(password)
    login_page.click_submit_button()

    # 3. Ждем ухода с /login
    WebDriverWait(driver, 15).until_not(
        EC.url_contains("/login")
    )

    # 4. Закрываем промо-окно, если оно всплыло сразу после логина
    dashboard_page.close_popup_if_exists()

    # 5. Ждем полной отрисовки интерфейса (заголовка "Мои деньги")
    WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located(dashboard_page.MY_MONEY_HEADER)
    )

    print("[AUTH SETUP] Авторизация успешно завершена.")
    yield driver

@pytest.fixture(scope="function")
def account_cleanup_registry(logged_in_driver):
    """
    Фикстура-реестр для автоматической очистки созданных счетов после теста.
    В самом тесте достаточно написать: account_cleanup_registry.append(name)
    """
    # То, что ДО yield — это Setup (выполняется до теста). Создаем пустой список для имен счетов.
    accounts_to_delete = []
    
    yield accounts_to_delete
    
    # То, что ПОСЛЕ yield — это Teardown (выполняется строго ПОСЛЕ завершения теста)
    if accounts_to_delete:
        print("\n[TEARDOWN] Фикстура поймала созданные счета. Начинаем автоматическую очистку...")
        dashboard_page = DashboardPage(logged_in_driver)
        accounts_page = AccountsMainPage(logged_in_driver)
        
        # Мягко возвращаемся в раздел счетов, если тест завершился в другом месте сайта
        if not accounts_page.is_page_loaded():
            dashboard_page.open_accounts_section()
            
        for account_name in accounts_to_delete:
            try:
                print(f"[TEARDOWN] Удаляем созданный в тесте счет: '{account_name}'")
                accounts_page.click_three_dots_for_account(account_name)
                accounts_page.click_delete_account_in_dropdown()
                accounts_page.click_confirm_delete_first_stage()
                accounts_page.tick_both_delete_checkboxes()
                accounts_page.click_confirm_delete_final_stage()
                print(f"[TEARDOWN] Счет '{account_name}' успешно удален.")
            except Exception as e:
                # В фикстуре очистки мы не пишем assert, чтобы не завалить основной тест,
                # если вдруг шторка удаления просто долго погружалась.
                print(f"[TEARDOWN] Предупреждение: Не удалось удалить '{account_name}'. Ошибка: {e}")