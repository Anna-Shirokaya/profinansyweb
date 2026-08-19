import time
import allure
from selenium.webdriver.common.by import By
from pages.dashboard_pages.dashboard_page import DashboardPage
from pages.debit_pages.accounts_main_page import AccountsMainPage

@allure.feature("Бюджет и Счета")
@allure.story("Управление дебетовыми счетами")
@allure.title("Успешное создание счёта с кастомной банковской иконкой в USD и начальным балансом")
def test_success_create_account_with_bank_icon(logged_in_driver, account_cleanup_registry):
    dashboard_page = DashboardPage(logged_in_driver)
    accounts_page = AccountsMainPage(logged_in_driver)
    
    # 1. Переходим в раздел "Счета"
    with allure.step("Перейти в раздел 'Счета' через главное меню"):
        assert dashboard_page.is_my_money_header_visible()
        dashboard_page.open_accounts_section()
        assert accounts_page.is_page_loaded()
    
    # 2. Открываем форму создания счета
    accounts_page.click_create_account_button()
    accounts_page.select_debit_account_type()
    accounts_page.click_continue_if_exists()
    
    # 3. Вводим название счета
    test_account_name = f"USD Банк-{int(time.monotonic())}"
    accounts_page.enter_account_name(test_account_name)
    
    # Регистрируем в реестр авто-удаления (Teardown сработает в любом случае!)
    account_cleanup_registry.append(test_account_name)
    
    # 4. Вводим кастомный начальный баланс 150,78
    accounts_page.enter_balance("150,78")
    
    # 5. Выбираем валюту "Доллар США"
    accounts_page.select_currency_by_name("Доллар США")
    
    # 6. Настраиваем оформление (выбираем банковскую иконку)
    accounts_page.open_icon_selection()
    accounts_page.click_banks_tab()
    accounts_page.select_first_bank_icon()
    
    # 7. Сохраняем счет
    accounts_page.click_save_button()
    
    # 8. Ожидаем базовое появление счета в сетке
    accounts_page.wait_until_account_created(test_account_name)
    
    # 9. СТРОГИЕ ПРОВЕРКИ ИКОНКИ, ВАЛЮТЫ И СУММЫ (ASSERTS)
    accounts_page.check_card_with_icon_and_usd(test_account_name)
    
    time.sleep(1)
    print(f"\n[ТЕСТ] Проверка завершена! Счет '{test_account_name}' содержит иконку, баланс 150,78 и значок $. ")