import time
import allure
from selenium.webdriver.common.by import By
from pages.dashboard_pages.dashboard_page import DashboardPage
from pages.debit_pages.accounts_main_page import AccountsMainPage

@allure.feature("Бюджет и Счета")
@allure.story("Управление дебетовыми счетами")
@allure.title("Успешное создание счёта с максимальным балансом и стандартной иконкой")
def test_success_create_account_with_max_balance_and_regular_icon(logged_in_driver, account_cleanup_registry):
    dashboard_page = DashboardPage(logged_in_driver)
    accounts_page = AccountsMainPage(logged_in_driver)
    
    # 1. Переходим в раздел "Счета"
    with allure.step("Перейти в раздел 'Счета' через главное меню"):
        assert dashboard_page.is_my_money_header_visible()
        dashboard_page.open_accounts_section()
        assert accounts_page.is_page_loaded()
    
    # 2. Открываем форму создания нового дебетового счета
    accounts_page.click_create_account_button()
    accounts_page.select_debit_account_type()
    accounts_page.click_continue_if_exists()
    
    # 3. Вводим уникальное название счета
    test_account_name = f"Макс Баланс-{int(time.monotonic())}"
    accounts_page.enter_account_name(test_account_name)
    
    # РЕГИСТРИРУЕМ В РЕЕСТР АВТО-УДАЛЕНИЯ (Teardown сотрет счет в конце теста)
    account_cleanup_registry.append(test_account_name)
    
    # 4. Вводим кастомный максимальный баланс 999 999 999 999.99 рублей
    accounts_page.enter_balance("999 999 999 999.99")
    
    # 5. Выбираем первую дефолтную валюту (Рубль)
    accounts_page.select_first_currency()
    
    # 6. Настраиваем оформление: выбираем первую стандартную иконку (лапку)
    accounts_page.open_icon_selection()
    accounts_page.select_first_regular_icon()
    
    # 7. Настраиваем цвет: кликаем на блок "Цвет иконки" и выбираем первый (серый)
    accounts_page.open_color_selection()
    accounts_page.select_first_color()
    
    # 8. Сохраняем счет
    accounts_page.click_save_button()
    
    # 9. Ожидаем, пока счет появится на карусели главного экрана
    accounts_page.wait_until_account_created(test_account_name)
    
    # 10. Проверяем баланс и иконку на главной карточке карусели
    accounts_page.check_card_with_huge_balance_and_icon(test_account_name)
    
    # ================= НОВЫЕ ШАГИ СЦЕНАРИЯ =================
    
    # 11. Кликаем на кнопку-иконку "Все счета" (кошелек рядом с настройками)
    accounts_page.click_all_accounts_button()
    
    # 12. Глубокая проверка счета внутри модального списка "Все счета"
    accounts_page.check_account_in_all_accounts_modal(test_account_name)

    with allure.step(f"Удалить созданный счет '{test_account_name}'"):
        accounts_page.click_three_dots_for_account(test_account_name)
        accounts_page.click_delete_account_in_dropdown()
        accounts_page.click_confirm_delete_first_stage()
        accounts_page.tick_both_delete_checkboxes()
        accounts_page.click_confirm_delete_final_stage()
        accounts_page.assert_account_is_deleted(test_account_name)
        
    
    time.sleep(1)
    print(f"\n[ТЕСТ] Полный триумф! Счет '{test_account_name}' проверен на карусели и в общем списке 'Все счета'.")