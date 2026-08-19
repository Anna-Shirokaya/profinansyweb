import time
import pytest
from pages.dashboard_pages.dashboard_page import DashboardPage
from pages.debit_pages.accounts_main_page import AccountsMainPage

@pytest.fixture(scope="function")
def prepared_debit_account(logged_in_driver):
    """
    Фикстура-фабрика: готовит дебетовый счет для редактирования.
    Передает в тест словарь account_data. Если тест переименует счет,
    он должен обновить значение account_data['name'], чтобы teardown отработал корректно.
    """
    dashboard_page = DashboardPage(logged_in_driver)
    accounts_page = AccountsMainPage(logged_in_driver)
    
    base_account_name = f"Счет-Редакт-{int(time.monotonic())}"
    print(f"\n[SETUP LOCAL] Создаем счет для модификации: '{base_account_name}'")
    
    # 1. Переходим и ЖДЕМ стабилизации интерфейса React
    dashboard_page.open_accounts_section()
    assert accounts_page.is_page_loaded(), "[FIXTURE SETUP] Страница счетов не загрузилась!"
    
    # 2. Теперь кликаем по стабильной кнопке
    accounts_page.click_create_account_button()
    accounts_page.select_debit_account_type()
    accounts_page.click_continue_if_exists()
    accounts_page.enter_account_name(base_account_name)
    accounts_page.enter_balance("500")
    accounts_page.select_first_currency()
    accounts_page.open_icon_selection()
    accounts_page.select_first_regular_icon()
    accounts_page.open_color_selection()
    accounts_page.select_first_color()
    accounts_page.click_save_button()
    accounts_page.wait_until_account_created(base_account_name)
    
    # ПЕРЕДАЕМ ДИНАМИЧЕСКИЙ СЛОВАРЬ В ТЕСТ
    account_data = {"name": base_account_name}
    yield account_data
    
    # ТЕЙРДАУН: Берет имя, актуальное на момент окончания теста
    current_name = account_data["name"]
    print(f"\n[TEARDOWN LOCAL] Начинаем автоматическое удаление счета: '{current_name}'")
    
    if not accounts_page.is_page_loaded():
        dashboard_page.open_accounts_section()
        
    try:
        accounts_page.click_three_dots_for_account(current_name)
        accounts_page.click_delete_account_in_dropdown()
        accounts_page.click_confirm_delete_first_stage()
        accounts_page.tick_both_delete_checkboxes()
        accounts_page.click_confirm_delete_final_stage()
        print(f"[TEARDOWN LOCAL] Счет '{current_name}' успешно удален.")
    except Exception as e:
        print(f"[TEARDOWN LOCAL] Предупреждение: Не удалось выполнить авто-удаление. Ошибка: {e}")