import allure
from pages.dashboard_pages.dashboard_page import DashboardPage
from pages.debit_pages.accounts_main_page import AccountsMainPage

@allure.feature("Бюджет и Счета")
@allure.story("Визуальное тестирование (Скриншоты)")
@allure.title("Проверка вёрстки пустого состояния страницы счетов по скриншоту-эталону")
def test_account_empty_state_visual_by_screenshot(logged_in_driver):
    dashboard_page = DashboardPage(logged_in_driver)
    accounts_page = AccountsMainPage(logged_in_driver)
    
    # 1. Переходим в раздел "Счета"
    with allure.step("Перейти в раздел 'Счета' через главное меню"):
        assert dashboard_page.is_my_money_header_visible(), "Главная страница дашборда не загрузилась!"
        dashboard_page.open_accounts_section()
        assert accounts_page.is_page_loaded(), "Раздел 'Счета' не открылся!"
    
    # 2. Запускаем строгую попиксельную проверку экрана по фото-эталону
    accounts_page.verify_visual_screenshot("account_empty_state_baseline")