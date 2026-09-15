import time
import allure
from selenium.webdriver.common.by import By
from pages.dashboard_pages.dashboard_page import DashboardPage
from pages.debit_pages.accounts_main_page import AccountsMainPage

@allure.feature("Бюджет и Счета")
@allure.story("Управление дебетовыми счетами")
@allure.title("Успешное создание счёта без ввода начального баланса")
# Добавили нашу новую фикстуру в аргументы функции:
def test_success_create_account_without_initial_balance(api_logged_in_driver, account_cleanup_registry):
    driver = api_logged_in_driver
    dashboard_page = DashboardPage(driver)
    accounts_page = AccountsMainPage(driver)

    # 1. Закрываем модалки и онбординг, если вылезли после входа
    accounts_page.close_budget_interface_modal_if_present()
    accounts_page.close_promo_popup_if_present()
    
    accounts_page.click_create_account_button()
    accounts_page.select_debit_account_type()
    accounts_page.click_continue_if_exists()
    
    # Генерируем уникальное имя, чтобы тесты не пересекались по данным
    test_account_name = f"Автотест-{int(time.monotonic())}"
    accounts_page.enter_account_name(test_account_name)
    
    # РЕГИСТРИРУЕМ СЧЕТ НА УДАЛЕНИЕ:
    account_cleanup_registry.append(test_account_name)
    
    accounts_page.select_first_currency()
    accounts_page.click_save_button()
    
    accounts_page.wait_until_account_created(test_account_name)
    
    with allure.step("Проверить, что на странице отображаются карточки счетов"):
        all_acc_card = api_logged_in_driver.find_element(By.XPATH, "//*[text()='Все счета']")
        new_acc_card = api_logged_in_driver.find_element(By.XPATH, f"//*[text()='{test_account_name}']")
        assert all_acc_card.is_displayed()
        assert new_acc_card.is_displayed()

    accounts_page.check_card_details(test_account_name)
    print("\n[ТЕСТ] Основные проверки создания счета завершены успешно!")