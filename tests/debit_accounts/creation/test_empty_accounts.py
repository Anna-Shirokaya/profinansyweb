import time
from pages.dashboard_pages.dashboard_page import DashboardPage
from pages.debit_pages.accounts_main_page import AccountsMainPage

def test_user_can_navigate_to_debit_accounts_and_see_empty_state(logged_in_driver):
    dashboard_page = DashboardPage(logged_in_driver)
    accounts_page = AccountsMainPage(logged_in_driver)
    
    # 1. Проверяем, что успешно попали на дашборд после авто-входа
    assert dashboard_page.is_my_money_header_visible(), "Не удалось загрузить дашборд после входа!"
    
    # 2. Раскрываем меню "Бюджет" и кликаем на "Счета"
    dashboard_page.open_accounts_section()
    
    # 3. Проверяем, что URL сменился на нужный раздел
    assert accounts_page.is_page_loaded(), "Ошибка: Раздел 'Счета' не загрузился!"
    
    # === НОВЫЕ ПРОВЕРКИ ТЕКСТА И КНОПОК ===
    
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