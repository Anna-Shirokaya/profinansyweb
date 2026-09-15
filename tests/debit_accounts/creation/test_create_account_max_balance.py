import time
import allure
from pages.dashboard_pages.dashboard_page import DashboardPage
from pages.debit_pages.accounts_main_page import AccountsMainPage

@allure.feature("Бюджет и Счета")
@allure.story("Управление дебетовыми счетами")
@allure.title("Успешное создание счёта с максимальным балансом и стандартной иконкой")
def test_success_create_account_with_max_balance_and_regular_icon(api_logged_in_driver, account_cleanup_registry):
    driver = api_logged_in_driver
    dashboard_page = DashboardPage(driver)
    accounts_page = AccountsMainPage(driver)
    
    # 1. Закрываем модалки и онбординг, если вылезли после входа
    accounts_page.close_budget_interface_modal_if_present()
    accounts_page.close_promo_popup_if_present()
    
    # 2. Открываем форму создания нового дебетового счета
    accounts_page.click_create_account_button()
    accounts_page.select_debit_account_type()
    accounts_page.click_continue_if_exists()
    
    # 3. Вводим уникальное название счета и регистрируем в реестр очистки
    test_account_name = f"Макс Баланс-{int(time.monotonic())}"
    accounts_page.enter_account_name(test_account_name)
    account_cleanup_registry.append(test_account_name)
    
    # 4. Вводим баланс, выбираем валюту, иконку и цвет
    accounts_page.enter_balance("999 999 999 999.99")
    accounts_page.select_first_currency()
    accounts_page.open_icon_selection()
    accounts_page.select_first_regular_icon()
    accounts_page.open_color_selection()
    accounts_page.select_first_color()
    
    # 5. Сохраняем счет
    accounts_page.click_save_button()
    
    # 6. Ожидаем и проверяем карточку на карусели
    accounts_page.wait_until_account_created(test_account_name)
    accounts_page.check_card_with_huge_balance_and_icon(test_account_name)
    
    # 7. Проверка в общем списке "Все счета"
    accounts_page.click_all_accounts_button()
    accounts_page.check_account_in_all_accounts_modal(test_account_name)

    print(f"\n[ТЕСТ] Успешно! Счет '{test_account_name}' проверен на карусели и в списке 'Все счета'.")