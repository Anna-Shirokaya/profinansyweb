import time
import allure
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.dashboard_pages.dashboard_page import DashboardPage
from pages.debit_pages.accounts_main_page import AccountsMainPage
from pages.transactions_pages.transactions_modal_page import TransactionsModalPage


@allure.feature("Бюджет и Счета")
@allure.story("Транзакции - Расход")
@allure.testcase("WAL-T519", "WAL-T519: Создание транзакции на расход только с типом, без названия")
@allure.title("[WAL-T519] Создание транзакции на расход с новым типом расхода")
def test_create_expense_transaction_with_new_type_wal_t519(api_logged_in_driver, api_created_debit_account):
    driver = api_logged_in_driver
    account_name = api_created_debit_account
    new_type_name = "Новое название для теста создания транзакций на расход"
    amount_value = "1050.89"

    dashboard_page = DashboardPage(driver)
    accounts_page = AccountsMainPage(driver)
    transaction_modal = TransactionsModalPage(driver)

    # 1. Подготовка страницы и выбор счета
    accounts_page.close_budget_interface_modal_if_present()
    accounts_page.close_promo_popup_if_present()
    driver.refresh()
    accounts_page.wait_until_account_created(account_name)

    with allure.step(f"Выделить карточку счета '{account_name}'"):
        accounts_page.click_account_card_by_name(account_name)
        time.sleep(0.5)

    # 2. Открытие формы добавления транзакции
    with allure.step("Нажать кнопку '+ Добавить операцию'"):
        dashboard_page.open_add_transaction_modal()

    # 3. Ввод суммы и проверка разделителя разрядов (1050,89)
    with allure.step(f"Ввести сумму {amount_value}"):
        amount_input = driver.find_element(*transaction_modal.AMOUNT_INPUT)
        amount_input.click()
        amount_input.clear()
        amount_input.send_keys(amount_value)
        
        # Проверяем отображение разделителя разрядов
        current_amount_val = amount_input.get_attribute("value")
        assert "1050,89" in current_amount_val or "1 050,89" in current_amount_val, (
            f"Форматирование суммы неверно! Получено: {current_amount_val}"
        )

    # 4. Создание нового типа расхода из модалки
    with allure.step("Открыть форму создания типа расхода и заполнить данные"):
        transaction_modal.open_create_expense_type_modal()
        transaction_modal.create_new_expense_type(type_name=new_type_name, category="Переменные")

    # Гарантированная очистка созданного типа расхода в случае успеха или падения теста
    try:
        # 5. Сохранение транзакции
        with allure.step("Нажать 'Создать' транзакцию"):
            transaction_modal.click_submit_button()

        # 6. Проверка истории операций на дашборде
        with allure.step("Проверить созданную транзакцию в истории операций"):
            dashboard_page.verify_transaction_in_history(
                type_name=new_type_name,
                expected_amount="1050,89",
                expected_account_name=account_name
            )

        print(f"\n[ТЕСТ WAL-T519] Транзакция с новым типом '{new_type_name}' успешно создана и проверена.")

        # 7. Проверка фильтрации по вкладкам (Доходы, Переводы, Накопления)
        with allure.step("Проверить отсутствие транзакции во вкладках 'Доходы', 'Переводы', 'Накопления'"):
            for tab_name in ["Доходы", "Переводы", "Накопления"]:
                dashboard_page.switch_history_tab(tab_name)
                dashboard_page.verify_history_is_empty()

        print(f"\n[ТЕСТ WAL-T519] Транзакция с новым типом '{new_type_name}' успешно создана и проверена во всех вкладках.")

    finally:
        # Выполняется ВСЕГДА: удаляет тип расхода в Настройках
        with allure.step(f"Очистка: удалить созданный тип расхода '{new_type_name}'"):
            try:
                
                dashboard_page.delete_expense_type(new_type_name)
            except Exception as e:
                print(f"[TEARDOWN WARNING] Не удалось удалить тип расхода: {e}")