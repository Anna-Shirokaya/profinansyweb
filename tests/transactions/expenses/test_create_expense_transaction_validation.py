import allure
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from pages.dashboard_pages.dashboard_page import DashboardPage
from pages.debit_pages.accounts_main_page import AccountsMainPage
from pages.transactions_pages.transactions_modal_page import TransactionsModalPage


@allure.feature("Бюджет и Счета")
@allure.story("Транзакции - Расход")
@allure.testcase("WAL-T518", "WAL-T518: Проверка полей формы создания транзакции расхода и ошибок валидации")
@allure.title("[WAL-T518] Проверка полей формы создания транзакции на расход и ошибки при незаполненных обязательных полях")
def test_expense_transaction_form_validation_wal_t518(api_logged_in_driver, api_created_debit_account):
    driver = api_logged_in_driver
    account_name = api_created_debit_account
    
    dashboard_page = DashboardPage(driver)
    accounts_page = AccountsMainPage(driver)
    transaction_modal = TransactionsModalPage(driver)

    # 1. Закрываем модалки и обновляем DOM для отображения API-счета
    accounts_page.close_budget_interface_modal_if_present()
    accounts_page.close_promo_popup_if_present()
    
    driver.refresh()
    accounts_page.wait_until_account_created(account_name)

    # 2. Выделяем нужный счёт
    print("\n[LOG 1] Начинаем вызов click_account_card_by_name...")
    with allure.step(f"Выделить карточку счета '{account_name}'"):
        accounts_page.click_account_card_by_name(account_name)
    print(f"[LOG 2] Карточка выделена. Текущий URL: {driver.current_url}")

    # Фиксируем открытые модальные окна в DOM сразу после выделения
    modals = driver.find_elements(By.CSS_SELECTOR, ".sideModal-title, [role='dialog'] h2, h3")
    print(f"[LOG 3] Видимые заголовки модалок после клика на карточку: {[m.text for m in modals if m.is_displayed()]}")

    time.sleep(1)  # Пауза для фиксации возможного фонового события React

    # 3. Открываем модалку транзакции
    print("[LOG 4] Вызываем open_add_transaction_modal...")
    with allure.step("Нажать кнопку '+ Добавить операцию'"):
        dashboard_page.open_add_transaction_modal()
    print("[LOG 5] Кнопка '+ Добавить операцию' нажата.")

    # Проверяем заголовки модалок до запуска верификации
    modals_after_add = driver.find_elements(By.CSS_SELECTOR, ".sideModal-title, [role='dialog'] h2, h3")
    print(f"[LOG 6] Заголовки модалок сразу после нажатия '+ Добавить операцию': {[m.text for m in modals_after_add if m.is_displayed()]}")

    time.sleep(1.5)

    # Проверяем заголовки модалок перед проверкой полей
    modals_before_verify = driver.find_elements(By.CSS_SELECTOR, ".sideModal-title, [role='dialog'] h2, h3")
    print(f"[LOG 7] Заголовки модалок через 1.5 сек (перед verify_expense_form_elements): {[m.text for m in modals_before_verify if m.is_displayed()]}")

    # 4. Проверяем элементы формы расхода
    print("[LOG 8] Запуск verify_expense_form_elements...")
    transaction_modal.verify_expense_form_elements(expected_account_name=account_name)
    print("[LOG 9] Валидация элементов завершена успешно.")