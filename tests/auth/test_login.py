import os  # Импортируем стандартный модуль для работы с ОС
from pages.auth_pages.welcome_page import WelcomePage
from pages.auth_pages.login_page import LoginPage
from pages.dashboard_pages.dashboard_page import DashboardPage

def test_user_can_login_successfully(driver):
    welcome_page = WelcomePage(driver)
    login_page = LoginPage(driver)
    dashboard_page = DashboardPage(driver)
    
    welcome_page.open()
    welcome_page.click_login_button()
    
    # Достаем секретные данные из файла .env через os.getenv
    email = os.getenv("PROFINANSY_USER_EMAIL")
    password = os.getenv("PROFINANSY_USER_PASSWORD")
    
    # Передаем скрытые переменные в методы страницы
    login_page.enter_email(email)
    login_page.enter_password(password)
    
    login_page.click_submit_button()
    
    # Проверка
    is_header_visible = dashboard_page.is_my_money_header_visible()
    assert is_header_visible, "Авторизация провалилась! Заголовок 'Мои деньги' не найден."
    
    print("\n[ТЕСТ] Сценарий авторизации выполнен безопасно!")