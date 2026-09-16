import time
from pages.dashboard_pages.dashboard_page import DashboardPage
from pages.debit_pages.accounts_main_page import AccountsMainPage

def test_user_can_navigate_to_debit_accounts_and_see_empty_state(api_logged_in_driver):
    driver = api_logged_in_driver
    accounts_page = AccountsMainPage(driver)
    
    # 1. Закрываем возможные оверлеи
    accounts_page.close_budget_interface_modal_if_present()
    accounts_page.close_promo_popup_if_present()
    
    # 4. Проверяем главный заголовок пустого состояния
    actual_title = accounts_page.get_empty_state_title_text()
    assert actual_title == "Здесь пока ничего нет", f"Ожидали один заголовок, но получили: '{actual_title}'"
    print("[ТЕСТ] Проверка заголовка 'Здесь пока ничего нет' — УСПЕШНО")

    # 5. Проверяем подзаголовок (описание)
    actual_desc = accounts_page.get_empty_state_description_text()
    expected_desc = "Чтобы начать пользоваться бюджетом, создайте счет"
    assert expected_desc in actual_desc, f"Текст описания не совпадает! На сайте написано: '{actual_desc}'"
    print("[ТЕСТ] Проверка текста описания бюджетов — УСПЕШНО")

    # 6. Проверяем, что кнопка добавления счета на месте
    assert accounts_page.is_create_account_btn_visible(), "Кнопка 'Создать счёт +' отсутствует на странице!"
    print("[ТЕСТ] Проверка видимости кнопки 'Создать счёт +' — УСПЕШНО")
 
    print("\n[ТЕСТ] Отлично! Весь блок пустого состояния проверен и соответствует требованиям.")