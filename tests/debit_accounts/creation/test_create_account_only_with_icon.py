import time
import allure
from pages.debit_pages.accounts_main_page import AccountsMainPage


@allure.feature("Бюджет и Счета")
@allure.story("Управление дебетовыми счетами")
@allure.title("Успешное создание счёта с кастомной банковской иконкой в USD и начальным балансом")
def test_success_create_account_with_bank_icon(api_logged_in_driver, account_cleanup_registry):
    driver = api_logged_in_driver
    accounts_page = AccountsMainPage(driver)
    
    # 1. Закрываем модалки и онбординг
    accounts_page.close_budget_interface_modal_if_present()
    accounts_page.close_promo_popup_if_present()
    
    # 2. Открываем форму создания счета
    accounts_page.click_create_account_button()
    accounts_page.select_debit_account_type()
    accounts_page.click_continue_if_exists()
    
    # 3. Название счета и регистрация в авто-удаление
    test_account_name = f"USD Банк-{int(time.monotonic())}"
    accounts_page.enter_account_name(test_account_name)
    account_cleanup_registry.append(test_account_name)
    
    # 4. Баланс 150,78 и выбор валюты "Доллар США"
    accounts_page.enter_balance("150,78")
    accounts_page.select_currency_by_name("Доллар США")
    
    # 5. Выбор банковской иконки
    accounts_page.open_icon_selection()
    accounts_page.click_banks_tab()
    accounts_page.select_first_bank_icon()
    
    # 6. Сохранение счета
    accounts_page.click_save_button()
    
    # 7. Ожидание и проверка карточки
    accounts_page.wait_until_account_created(test_account_name)
    accounts_page.check_card_with_icon_and_usd(test_account_name)
    
    print(f"\n[ТЕСТ] Проверка завершена! Счет '{test_account_name}' содержит банковскую иконку, баланс 150,78 и значок $. ")