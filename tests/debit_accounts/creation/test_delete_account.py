import time
import pytest
import allure
from pages.debit_pages.accounts_main_page import AccountsMainPage


# === ФИКСТУРА ПРЕДУСТАНОВКИ (SETUP) ===
@pytest.fixture(scope="function")
def setup_debit_account(api_logged_in_driver):
    """Фикстура автоматического создания дебетового счета перед началом теста на удаление"""
    driver = api_logged_in_driver
    accounts_page = AccountsMainPage(driver)
    
    # Закрываем модалки и онбординг перед созданием
    accounts_page.close_budget_interface_modal_if_present()
    accounts_page.close_promo_popup_if_present()
    
    # Генерируем уникальное имя
    unique_account_name = f"Удаление-{int(time.monotonic())}"
    print(f"\n[FIXTURE SETUP] Создаем тестовый счет для последующего удаления: '{unique_account_name}'")
    
    # Шаги создания счета
    accounts_page.click_create_account_button()
    accounts_page.select_debit_account_type()
    accounts_page.click_continue_if_exists()
    accounts_page.enter_account_name(unique_account_name)
    accounts_page.select_first_currency()
    accounts_page.click_save_button()
    
    # Ждем появление карточки в DOM
    accounts_page.wait_until_account_created(unique_account_name)
    print("[FIXTURE SETUP] Тестовый счет успешно подготовлен.")
    
    yield unique_account_name


# === САМ ТЕСТ-КЕЙС ===
@allure.feature("Бюджет и Счета")
@allure.story("Управление дебетовыми счетами")
@allure.title("Успешное удаление дебетового счёта через двухэтапное подтверждение")
def test_success_delete_debit_account(api_logged_in_driver, setup_debit_account):
    target_account_name = setup_debit_account
    driver = api_logged_in_driver
    accounts_page = AccountsMainPage(driver)

    # 1. Закрываем возможные оверлеи
    accounts_page.close_budget_interface_modal_if_present()
    accounts_page.close_promo_popup_if_present()
    
    # 2. Нажимаем 3 точки на созданной карточке
    accounts_page.click_three_dots_for_account(target_account_name)
    
    # 3. Выбираем 'Удалить счет' в выпадающем списке
    accounts_page.click_delete_account_in_dropdown()
    
    # 4. Кликаем 'Удалить счет' в первом модальном окне предупреждения
    accounts_page.click_confirm_delete_first_stage()
    
    # 5. Проставляем оба чекбокса согласия во втором модальном окне
    accounts_page.tick_both_delete_checkboxes()
    
    # 6. Нажимаем финальную активировавшуюся кнопку 'Удалить счет'
    accounts_page.click_confirm_delete_final_stage()
    
    # 7. ГЛАВНАЯ ПРОВЕРКА (ASSERT): убеждаемся, что карточка пропала из интерфейса
    accounts_page.assert_account_is_deleted(target_account_name)
    
    print(f"\n[ТЕСТ] УСПЕХ! Счет '{target_account_name}' успешно удален со всеми шагами проверок.")