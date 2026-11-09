import time
import allure
import pytest
from selenium.webdriver.common.by import By

from pages.dashboard_pages.dashboard_page import DashboardPage
from pages.debit_pages.accounts_main_page import AccountsMainPage
from pages.transactions_pages.transactions_modal_page import TransactionsModalPage
from pages.transactions_pages.calculator_modal_page import CalculatorModalPage


@allure.feature("Бюджет и Счета")
@allure.story("Транзакции - Калькулятор")
@allure.testcase("WAL-T300", "WAL-T300: Проверка калькулятора и граничных значений")
@allure.title("[WAL-T300] Полная проверка функциональности и багов калькулятора")
def test_transaction_calculator_wal_t300(api_logged_in_driver, api_created_debit_account):
    driver = api_logged_in_driver
    account_name = api_created_debit_account

    dashboard_page = DashboardPage(driver)
    accounts_page = AccountsMainPage(driver)
    transaction_modal = TransactionsModalPage(driver)
    calc_page = CalculatorModalPage(driver)

    # 1. Подготовка страницы
    accounts_page.close_budget_interface_modal_if_present()
    accounts_page.close_promo_popup_if_present()
    driver.refresh()
    accounts_page.wait_until_account_created(account_name)

    # 2. Переход к созданию транзакции
    dashboard_page.open_add_transaction_modal()

    # --- ЧЕК 1: Проверка отсутствия нежелательной подсказки ---
    with allure.step("1. Проверить открытие калькулятора и отсутствие лишних подсказок"):
        calc_page.open_calculator()
        assert not calc_page.is_tooltip_present(), (
            "Баг: в калькуляторе отображается странная надпись 'Рекомендуется складывать сумму трат...'"
        )

    # --- ЧЕК 2: Ввод с клавиатуры ПК ---
    with allure.step("2. Проверить фокус и ввод с физической клавиатуры (25/5)"):
        calc_page.input_expression_via_keyboard("25/5=")
        display_val = calc_page.get_display_value()
        assert "5" in display_val, f"Ввод с клавиатуры не сработал! На дисплее: '{display_val}'"
        calc_page.click_ac()

    # --- ЧЕК 3: Ведущий ноль (Баг 5 - 015) ---
    with allure.step("3. Проверить расчет с ведущим нолем (5 - 015)"):
        calc_page.input_expression_via_mouse("5-015=")
        display_val = calc_page.get_display_value()
        assert display_val in ["-10", "-10,0"], f"Баг с ведущим нолем! Ожидалось -10, получено: '{display_val}'"
        calc_page.click_ac()

    # --- ЧЕК 4: Операции с десятичными дробями (2.5 + 0.5) ---
    with allure.step("4. Проверить сложение некруглых чисел (2.5 + 0.5)"):
        calc_page.input_expression_via_mouse("2.5+0.5=")
        display_val = calc_page.get_display_value()
        assert "3" in display_val and "25.5" not in display_val, f"Ошибка расчета дробей! Получено: '{display_val}'"
        calc_page.click_ac()

    # --- ЧЕК 5: Проценты (20 * 9%) ---
    with allure.step("5. Проверить расчет процентов (20 * 9%)"):
        calc_page.input_expression_via_mouse("20*9%=")
        display_val = calc_page.get_display_value()
        assert "1.8" in display_val or "1,8" in display_val, f"Ошибка расчета процентов! Получено: '{display_val}'"
        calc_page.click_ac()

    # --- ЧЕК 6: Отрицательные значения и валидация ошибок ---
    with allure.step("6. Проверить валидацию 'Сумма не может быть отрицательной' (5 - 10 = -5)"):
        calc_page.input_expression_via_mouse("5-10=")
        calc_page.click_apply_raw()
        
        error_msg = calc_page.get_error_text()
        assert "Сумма не может быть отрицательной" in error_msg, (
            f"Не появилось ожидаемое сообщение об ошибке! Получено: '{error_msg}'"
        )
        
        # Сбрасываем значение и закрываем калькулятор
        calc_page.click_ac()
        calc_page.apply_result()

    # --- ЧЕК 7: Вкладка 'Доход' ---
    with allure.step("7. Переключиться на вкладку 'Доход' и проверить калькулятор"):
        transaction_modal.open_income_tab()
        calc_page.open_calculator()
        calc_page.input_expression_via_mouse("100+50=")
        calc_page.apply_result()

        amount_val_income = driver.find_element(*transaction_modal.AMOUNT_INPUT).get_attribute("value")
        assert "150" in amount_val_income, f"Вкладка Доход: результат не подставился! Получено: '{amount_val_income}'"