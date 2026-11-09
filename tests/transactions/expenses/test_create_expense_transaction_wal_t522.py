import time
from datetime import datetime
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
@allure.testcase("WAL-T522", "WAL-T522: История после добавления транзакции на расход с названием и стандартным типом")
@allure.title("[WAL-T522] Создание транзакции на расход со стандартным типом 'Одежда'")
def test_create_expense_transaction_with_title_standard_type_wal_t522(api_logged_in_driver, api_created_debit_account):
    driver = api_logged_in_driver
    account_name = api_created_debit_account
    
    title_name = "Одежда"
    expense_type_name = "Одежда"
    amount_value = "10"
    comment_text = "тестирование заведения транзакции на расход на первый день текущего месяца"
    
    # Формируем дату первого дня текущего месяца (ДД.ММ.ГГГГ)
    first_day_date = datetime.now().replace(day=1).strftime("%d.%m.%Y")

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

    # 2. Открытие модального окна добавления транзакции
    with allure.step("Нажать кнопку '+ Добавить операцию'"):
        dashboard_page.open_add_transaction_modal()

    # 3. Заполнение формы транзакции через атомарные методы Page Object
    transaction_modal.enter_amount(amount_value)
    # 4. Вводим текст "Одежда" в поле
    transaction_modal.enter_title(title_name)

    # 5. Выбираем "Одежда" из появившегося списка подсказок
    transaction_modal.select_title_suggestion(title_name)

    with allure.step(f"Выбрать стандартный тип расхода '{expense_type_name}'"):
        transaction_modal.click_expense_type_field()
        transaction_modal.select_expense_type_from_dropdown(expense_type_name)

    # Открываем календарь и выбираем 1-е число месяца
    transaction_modal.open_date_picker()
    transaction_modal.select_day_from_calendar(1)

    transaction_modal.enter_comment(comment_text)

    # 4. Сохранение транзакции
    with allure.step("Нажать 'Создать'"):
        transaction_modal.click_submit_button()

    # 5. Проверка в истории операций (Вкладка 'Все')
    with allure.step("Проверить появление транзакции во вкладке 'Все'"):
        dashboard_page.verify_transaction_in_history(
            type_name=f"{expense_type_name} | {title_name}",
            expected_amount="10",
            expected_account_name=account_name
        )

    # 6. Проверка на вкладке 'Расходы'
    with allure.step("Перейти на вкладку 'Расходы' и проверить наличие транзакции"):
        dashboard_page.switch_history_tab("Расходы")
        dashboard_page.verify_transaction_in_history(
            type_name=f"{expense_type_name} | {title_name}",
            expected_amount="10",
            expected_account_name=account_name
        )

    print(f"\n[ТЕСТ WAL-T522] Транзакция '{expense_type_name} | {title_name}' на 10$ успешно создана и проверена во вкладках все и расходы!")