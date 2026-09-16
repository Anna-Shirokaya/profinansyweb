import allure
from pages.dashboard_pages.dashboard_page import DashboardPage
from pages.debit_pages.accounts_main_page import AccountsMainPage

@allure.feature("Бюджет и Счета")
@allure.story("Визуальное тестирование (Скриншоты)")
@allure.title("Проверка вёрстки пустого состояния страницы счетов по скриншоту-эталону")
def test_account_empty_state_visual_by_screenshot(api_logged_in_driver):
    driver = api_logged_in_driver
    accounts_page = AccountsMainPage(driver)

    # Закрываем модалки и онбординг, если вылезли после входа
    accounts_page.close_budget_interface_modal_if_present()
    accounts_page.close_promo_popup_if_present()
    
    # 2. Запускаем строгую попиксельную проверку экрана по фото-эталону
    accounts_page.verify_visual_screenshot("account_empty_state_baseline")