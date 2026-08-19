import allure
import time
from pages.dashboard_pages.dashboard_page import DashboardPage
from pages.debit_pages.accounts_main_page import AccountsMainPage

@allure.feature("Бюджет и Счета")
@allure.story("Управление дебетовыми счетами")
@allure.title("Проверка валидации: слишком длинное название счёта (>100 символов)")
def test_error_when_account_name_is_too_long(logged_in_driver):
    dashboard_page = DashboardPage(logged_in_driver)
    accounts_page = AccountsMainPage(logged_in_driver)
    
    with allure.step("Перейти в раздел 'Счета' через главное меню"):
        assert dashboard_page.is_my_money_header_visible(), "Не удалось загрузить дашборд!"
        dashboard_page.open_accounts_section()
        assert accounts_page.is_page_loaded(), "Раздел 'Счета' не загрузился!"
    
    with allure.step("Открыть форму создания и ввести слишком длинное название"):
        accounts_page.click_create_account_button()
        accounts_page.select_debit_account_type()
        accounts_page.click_continue_if_exists()
        
        long_name = "1" * 101
        accounts_page.enter_account_name(long_name)
        accounts_page.click_save_button()
    
    with allure.step("Проверить появление ошибки валидации"):
        assert accounts_page.is_too_long_error_visible(), "Ошибка 'Слишком длинное название' не отобразилась!"