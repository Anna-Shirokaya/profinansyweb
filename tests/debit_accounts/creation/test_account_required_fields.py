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
def test_required_fields_validation_on_account_creation(api_logged_in_driver):
    driver = api_logged_in_driver
    dashboard_page = DashboardPage(driver)
    accounts_page = AccountsMainPage(driver)
    
    # 2. Открываем форму создания дебетового счета
    accounts_page.click_create_account_button()
    accounts_page.select_debit_account_type()
    accounts_page.click_continue_if_exists()
    
    # 3. ПРОВЕРКА ИНДИКАТОРОВ (ЗВЁЗДОЧЕК)
    # 3. Проверка индикаторов обязательности (звёздочек) через Page Object
    name_label = accounts_page.get_account_name_label_text()
    currency_label = accounts_page.get_currency_label_text()
    
    assert "*" in name_label, f"У поля 'Название счета' нет красной звездочки! Текст: '{name_label}'"
    assert "*" in currency_label, f"У поля 'Валюта счета' нет красной звездочки! Текст: '{currency_label}'"
    
    # 4. Попытка сохранения пустой формы
    accounts_page.click_save_button()
    
    assert "*" in name_label, f"У поля 'Название счета' нет красной звездочки! Текст: '{name_label}'"
    assert "*" in currency_label, f"У поля 'Валюта счета' нет красной звездочки! Текст: '{currency_label}'"
    print("[ТЕСТ] Проверка наличия звёздочек у обязательных полей — УСПЕШНО")
