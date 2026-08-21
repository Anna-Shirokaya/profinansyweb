import time
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.dashboard_pages.dashboard_page import DashboardPage
from pages.debit_pages.accounts_main_page import AccountsMainPage


@allure.feature("Управление счетами")
@allure.story("Создание дебетового счета")
@allure.title("Проверка валидации обязательных полей (звёздочки и сообщения об ошибках)")
def test_required_fields_validation_on_account_creation(logged_in_driver):
    dashboard_page = DashboardPage(logged_in_driver)
    accounts_page = AccountsMainPage(logged_in_driver)
    
    # 1. Переходим в раздел "Счета"
    assert dashboard_page.is_my_money_header_visible(), "Не удалось загрузить дашборд!"
    dashboard_page.open_accounts_section()
    assert accounts_page.is_page_loaded(), "Раздел 'Счета' не загрузился!"
    
    # 2. Открываем форму создания дебетового счета
    accounts_page.click_create_account_button()
    accounts_page.select_debit_account_type()
    accounts_page.click_continue_if_exists()
    
    # 3. ПРОВЕРКА ИНДИКАТОРОВ (ЗВЁЗДОЧЕК)
    # Находим элемент "Название счета" напрямую через driver в обход Page Object
    name_label_element = WebDriverWait(logged_in_driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Название счета')]"))
    )
    name_label = name_label_element.text
    currency_label = accounts_page.get_currency_label_text()
    
    assert "*" in name_label, f"У поля 'Название счета' нет красной звездочки! Текст: '{name_label}'"
    assert "*" in currency_label, f"У поля 'Валюта счета' нет красной звездочки! Текст: '{currency_label}'"
    print("[ТЕСТ] Проверка наличия звёздочек у обязательных полей — УСПЕШНО")
    
    # 4. Кликаем на кнопку "Сохранить", оставив поля пустыми
    accounts_page.click_save_button()
    
    # 5. ПРОВЕРКА ТЕКСТА ОШИБОК ВАЛИДАЦИИ (ASSERTS)
    assert accounts_page.is_name_required_error_visible(), "Ошибка 'Обязательное поле' не появилась под названием счета!"
    assert accounts_page.is_currency_required_error_visible(), "Ошибка 'Обязательное поле' не появилась под валютой счета!"
    
    print("\n[ТЕСТ] Валидация незаполненных обязательных полей успешно пройдена!")