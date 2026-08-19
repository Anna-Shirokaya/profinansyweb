import time
import allure
from pages.debit_pages.accounts_main_page import AccountsMainPage

@allure.feature("Бюджет и Счета")
@allure.story("Модификация дебетовых счетов")
@allure.title("Изменение названия дебетового счета по клику на 3 точки")
def test_change_debit_account_name_via_three_dots(logged_in_driver, prepared_debit_account):
    # Извлекаем данные из фикстуры контекста
    account_data = prepared_debit_account
    old_name = account_data["name"]
    
    accounts_page = AccountsMainPage(logged_in_driver)
    new_name = f"НовоеИмя-{int(time.monotonic())}"
    
    # 1. Переходим в режим редактирования через меню "3 точки"
    accounts_page.click_three_dots_for_account(old_name)
    accounts_page.click_edit_account_in_dropdown()
    
    # 2. Переименовываем счет и сохраняем форму
    with allure.step(f"Ввести новое название счета: '{new_name}' и сохранить"):
        accounts_page.enter_account_name(new_name)
        accounts_page.click_save_button()
        
    # ВАЖНО: Сообщаем фикстуре очистки новое имя счета, чтобы она смогла удалить его после теста!
    account_data["name"] = new_name
        
    # 3. ПРОВЕРКА №1: Проверяем появление нового названия прямо на карточке счета в карусели
    with allure.step("Проверить, что новое название отображается на главной карточке счета"):
        accounts_page.wait_until_account_created(new_name)
    
    # 4. Переходим в окно "Все счета"
    accounts_page.click_all_accounts_button()
    
    # 5. ПРОВЕРКА №2: Проверяем отображение нового названия внутри открывшейся модалки
    accounts_page.assert_account_name_visible_in_modal(new_name)
    
    time.sleep(1)
    print(f"\n[ТЕСТ] Успех! Счет переименован в '{new_name}', изменения проверены на карточке и в списке.")