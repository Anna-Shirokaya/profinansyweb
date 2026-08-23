import time
import allure
import os
from PIL import Image, ImageChops

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException


class AccountsMainPage:
    def __init__(self, driver):
        self.driver = driver
        
        # ЛОКАТОРЫ СТРАНИЦЫ И ПУСТОГО СОСТОЯНИЯ
        self.EMPTY_STATE_TITLE = (By.XPATH, "//*[text()='Здесь пока ничего нет']")
        self.EMPTY_STATE_DESC = (By.XPATH, "//*[contains(text(), 'Чтобы начать пользоваться бюджетом')]")
        self.CREATE_ACCOUNT_BTN = (By.XPATH, "//button[contains(., 'Создать счёт')]")
        
        # ЛОКАТОРЫ ФОРМЫ СОЗДАНИЯ СЧЕТА
        self.DEBIT_TYPE_CARD = (By.XPATH, "//button[contains(., 'Дебетовый')] | //img[@alt='Дебетовый']/ancestor::button[1]")
        self.CONTINUE_BUTTON = (By.XPATH, "//button[contains(., 'Продолжить')] | //*[text()='Продолжить']")
        self.ACCOUNT_NAME_INPUT = (By.XPATH, "//input[@name='title' or @placeholder='Введите название']")
        self.BALANCE_INPUT = (By.XPATH, "//input[@name='balance']")
        # Локатор кликабельного контейнера поля валюты (соседний div после label)
        self.CURRENCY_SELECT_TRIGGER = (
            By.XPATH,
            "//*[contains(string(), 'Валюта счета')]/following::input[1] | "
            "//input[@placeholder='Выберите валюту из списка']"
        )
        # Динамический локатор пункта валюты в выпадающем списке <ul>
        self.CURRENCY_OPTION_BY_NAME = lambda name: (
            By.XPATH, 
            f"//li[@role='button' and text()='{name}'] | //ul[contains(@class, 'Selectstyled__List')]//li[text()='{name}']"
        )
        self.FIRST_CURRENCY_OPTION = (By.XPATH, "//div[contains(@class, 'Select-dropdown')]//li[1]")
        self.SAVE_BUTTON = (By.XPATH, "//button[contains(., 'Сохранить')] | //*[text()='Сохранить']")
        
        # ЛОКАТОРЫ ОШИБОК И ВАЛИДАЦИИ
        self.ACCOUNT_NAME_LABEL = (By.XPATH, "//*[contains(text(), 'Название счета')]")
        self.CURRENCY_LABEL = (By.XPATH, "//*[contains(text(), 'Валюта счета')]")
        self.TOO_LONG_ERROR_MSG = (By.XPATH, "//*[text()='Слишком длинное название']")
        self.NAME_REQUIRED_ERROR = (By.XPATH, "//*[contains(text(), 'Название счета')]/following::*[text()='Обязательное поле'][1]")
        self.CURRENCY_REQUIRED_ERROR = (By.XPATH, "//*[contains(text(), 'Валюта счета')]/following::*[text()='Обязательное поле'][1]")

        # ЛОКАТОРЫ ДЛЯ ОФОРМЛЕНИЯ И ИКОНОК
        self.ICON_SECTION_TRIGGER = (By.XPATH, "//*[text()='Иконка счета']/ancestor::div[1] | //*[contains(text(), 'Иконка счета')]")
        self.BANKS_TAB = (By.XPATH, "//*[text()='Банки'] | //button[contains(., 'Банки')]")
        self.FIRST_BANK_ICON = (By.XPATH, "(//span[@role='button' and @data-type='bank'])[1]")
        self.FIRST_REGULAR_ICON = (By.XPATH, "//*[contains(text(), 'Иконка счета')]/following::span[@role='button' and not(@data-type='bank')][1]")
        self.COLOR_SECTION_TRIGGER = (By.XPATH, "//*[text()='Цвет иконки']/ancestor::div[1] | //*[contains(text(), 'Цвет иконки')]")
        self.FIRST_COLOR_OPTION = (By.XPATH, "//*[contains(text(), 'Цвет иконки')]/following::span[@role='button'][1]")

        # ЛОКАТОРЫ ДЛЯ ОКНА "ВСЕ СЧЕТА"
        self.ALL_ACCOUNTS_BTN = (By.XPATH, "//div[contains(@class, 'ButtonsBlock')]//button[1]")
        self.ALL_ACCOUNTS_HEADER = (By.XPATH, "//*[text()='Все счета']")
        self.BTN_EDIT_IN_DROPDOWN = (By.XPATH, "//span[text()='Настроить счет']")
        # Динамический локатор строки счета в модальном окне "Все счета"
        self.MODAL_ACCOUNT_CARD_BY_NAME = lambda name: (
            By.XPATH, f"//span[contains(text(), '{name}')]/ancestor::div[contains(@class, 'AccountListCardstyled__Root')][1]"
        )

        # ЛОКАТОРЫ ПРОЦЕССА УДАЛЕНИЯ СЧЕТА
        self.DELETE_DROPDOWN_ITEM = (By.XPATH, "//button[@class='removeBtn'] | //*[text()='Удалить счет']")
        self.CONFIRM_DELETE_FIRST_BTN = (By.XPATH, "//button[contains(., 'Удалить счет')]")
        self.DELETE_CHECKBOX_1 = (By.XPATH, "//*[contains(text(), 'Я понимаю, что удаление счета')]")
        self.DELETE_CHECKBOX_2 = (By.XPATH, "//*[contains(text(), 'Я осознаю, что мое решение')]")
        self.CONFIRM_DELETE_FINAL_BTN = (By.XPATH, "//div[contains(@class, 'DeleteAccountModal')]//button[contains(., 'Удалить счет')] | (//button[contains(., 'Удалить счет')])[last()]")

        # Универсальный локатор крестиков во всех всплывающих окнах и модалках
        self.PROMO_CLOSE_BTN = (
        By.XPATH,
        "//*[contains(@class, 'close') or contains(@class, 'Close') or @aria-label='Закрыть' or @aria-label='Close'] | "
        "//*[contains(@class, 'modal') or contains(@class, 'Modal') or contains(@class, 'popup') or contains(@class, 'overlay')]//*[self::button or self::div or self::span][.//svg or contains(@class, 'close') or contains(@class, 'Close')]"
    )

        # Точечные динамические локаторы карточки и её трех точек
        self.ACCOUNT_CARD_BY_NAME = lambda name: (
            By.XPATH, f"//p[contains(text(), '{name}')]/ancestor::div[contains(@class, 'AccountCardstyled__Root')][1]"
        )
        self.THREE_DOTS_BY_NAME = lambda name: (
            By.XPATH, f"//p[contains(text(), '{name}')]/ancestor::div[contains(@class, 'AccountCardstyled__Root')][1]//button[@aria-haspopup='dialog']"
        )

        # Универсальный локатор закрытия баннеров
        self.PROMO_CLOSE_BTN = (
            By.XPATH,
            "//button[@aria-label='Закрыть' or @aria-label='Close'] | "
            "//*[contains(@class, 'Modal') or contains(@class, 'modal') or contains(@class, 'popup') or contains(@class, 'overlay')]//button[.//svg or contains(@class, 'close') or contains(@class, 'Close')]"
        )

    def is_page_loaded(self) -> bool:
        """Проверяет успешную загрузку раздела счетов"""
        try:
            WebDriverWait(self.driver, 15).until(
                EC.url_contains("/wallet/accounts")
            )
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located(self.CREATE_ACCOUNT_BTN)
            )
            return True
        except Exception as e:
            print(f"\n[DEBUG ERROR] is_page_loaded не дождался загрузки!")
            print(f"[DEBUG ERROR] Текущий URL: {self.driver.current_url}")
            print(f"[DEBUG ERROR] Текст ошибки: {e}")
            return False

    def get_empty_state_title_text(self) -> str:
        element = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(self.EMPTY_STATE_TITLE))
        return element.text

    def get_empty_state_description_text(self) -> str:
        element = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(self.EMPTY_STATE_DESC))
        return element.text

    def is_create_account_btn_visible(self) -> bool:
        try:
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(self.CREATE_ACCOUNT_BTN))
            return True
        except TimeoutException:
            return False

    # === РАБОТА С ФОРМОЙ СОЗДАНИЯ ===

    @allure.step("Нажать кнопку 'Создать счёт +'")
    def click_create_account_button(self):
        """Нажатие кнопки 'Создать счёт' с защитой от re-render в React"""
        for _ in range(3):
            try:
                btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(self.CREATE_ACCOUNT_BTN)
                )
                self.driver.execute_script("arguments[0].click();", btn)
                break
            except StaleElementReferenceException:
                continue

    @allure.step("Выбрать тип счёта 'Дебетовый'")
    def select_debit_account_type(self):
        """Выбор дебетовой карточки через клик по тегу <button>"""
        card_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.DEBIT_TYPE_CARD)
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card_button)
        
        try:
            card_button.click()
            print("[DEBIT PAGE] Выбран тип счёта: Дебетовый (обычный клик по button)")
        except Exception:
            self.driver.execute_script("arguments[0].click();", card_button)
            print("[DEBIT PAGE] Выбран тип счёта: Дебетовый (JS-клик по button)")
            
        time.sleep(0.5)

    @allure.step("Обработать переход к вводу названия счёта")
    def click_continue_if_exists(self):
        """Умный переход: дожидаемся активности кнопки 'Продолжить' и переходим на Шаг 2"""
        try:
            WebDriverWait(self.driver, 2).until(
                EC.visibility_of_element_located(self.ACCOUNT_NAME_INPUT)
            )
            print("[DEBIT PAGE] Шаг 2 уже открыт (кнопка 'Продолжить' не потребовалась)")
            return
        except TimeoutException:
            pass

        try:
            btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(self.CONTINUE_BUTTON)
            )
            try:
                btn.click()
            except Exception:
                self.driver.execute_script("arguments[0].click();", btn)
                
            print("[DEBIT PAGE] Успешно нажата кнопка 'Продолжить'")
            
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(self.ACCOUNT_NAME_INPUT)
            )
        except TimeoutException:
            raise AssertionError("[DEBIT PAGE] Ошибка: Форма не перешла на Шаг 2 за 10 секунд!")

    @allure.step("Ввести название счёта: {account_name}")
    def enter_account_name(self, account_name: str):
        """Ввод имени счета с ожиданием отрисовки элемента в React"""
        name_input = WebDriverWait(self.driver, 15).until(
            EC.visibility_of_element_located(self.ACCOUNT_NAME_INPUT)
        )
        
        try:
            name_input.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", name_input)
            
        name_input.clear()
        name_input.send_keys(account_name)
        print(f"[DEBIT PAGE] Успешно введено название счета: '{account_name}'")

    @allure.step("Ввести начальный баланс: {balance_text}")
    def enter_balance(self, balance_text: str):
        """Вводит сумму в поле 'Баланс'"""
        input_field = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.BALANCE_INPUT)
        )
        
        try:
            input_field.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", input_field)
            
        input_field.send_keys(Keys.CONTROL + "a")
        input_field.send_keys(Keys.BACKSPACE)
        input_field.send_keys(balance_text)
        print(f"[DEBIT PAGE] Введен баланс счета: {balance_text}")

    @allure.step("Выбрать первую валюту из выпадающего списка")
    def select_first_currency(self):
        currency_trigger = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.CURRENCY_SELECT_TRIGGER))
        try:
            currency_trigger.click()
            print("[DEBIT PAGE] Раскрыли список валют обычным кликом.")
        except Exception:
            print("[DEBIT PAGE] Обычный клик перехвачен, открываем селект через JavaScript...")
            self.driver.execute_script("arguments[0].click();", currency_trigger)
        
        first_option = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(self.FIRST_CURRENCY_OPTION))
        try:
            first_option.click()
            print("[DEBIT PAGE] Выбрана первая опция списка обычным кликом.")
        except Exception:
            print("[DEBIT PAGE] Клик по опции перехвачен, выбираем через JavaScript...")
            self.driver.execute_script("arguments[0].click();", first_option)

    @allure.step("Выбрать валюту '{currency_name}' из выпадающего списка")
    def select_currency_by_name(self, currency_name: str):
        """Открывает список валют с паузами и подробным логированием каждого шага для отладки"""
        print("\n[DEBUG] --- НАЧАЛО ВЫБОРА ВАЛЮТЫ ---")
        self.close_promo_popup_if_present()
        
        for attempt in range(3):
            try:
                print(f"[DEBUG] Попытка {attempt + 1}: Ожидаем появление поля валюты в DOM...")
                currency_trigger = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(self.CURRENCY_SELECT_TRIGGER)
                )
                print("[DEBUG] Поле найдено. Выполняем скролл к нему...")
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", currency_trigger)
                
                print("[DEBUG] ⏳ Пауза 2 сек: Посмотрите на экран. Видно ли поле? Перекрыто ли оно чем-то?")
                time.sleep(2)
                
                print("[DEBUG] Пробуем кликнуть по полю для открытия списка...")
                try:
                    currency_trigger.click()
                    print("[DEBUG] Успешно выполнен обычный Selenium-клик.")
                except Exception as e:
                    print(f"[DEBUG] Обычный клик заблокирован: {e}. Пробуем JS-клик...")
                    self.driver.execute_script("arguments[0].click();", currency_trigger)
                    print("[DEBUG] JS-клик выполнен.")
                
                print("[DEBUG] ⏳ Пауза 2 сек: Посмотрите на экран. Открылся ли выпадающий список?")
                time.sleep(2)
                break
            except StaleElementReferenceException:
                print("[DEBUG] Элемент устарел (StaleElementReferenceException) из-за перерендера. Повторяем поиск...")
                time.sleep(1)
                if attempt == 2:
                    raise
            except Exception as e:
                print(f"[DEBUG] КРИТИЧЕСКАЯ ОШИБКА при поиске поля: {e}")
                raise

        print(f"[DEBUG] Ищем пункт с названием валюты '{currency_name}'...")
        try:
            # Используем presence вместо visibility на случай, если список перекрыт другим невидимым слоем
            option = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(self.CURRENCY_OPTION_BY_NAME(currency_name))
            )
            print("[DEBUG] Пункт валюты найден в коде. Скроллим к нему...")
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'nearest'});", option)
            
            print("[DEBUG] ⏳ Пауза 1 сек перед кликом по валюте...")
            time.sleep(1)
            
            try:
                option.click()
                print("[DEBUG] Обычный клик по пункту валюты прошел успешно.")
            except Exception:
                print("[DEBUG] Обычный клик не удался, делаем JS-клик по пункту.")
                self.driver.execute_script("arguments[0].click();", option)
                
            print(f"[DEBIT PAGE] Успешно выбрана валюта: '{currency_name}'")
            print("[DEBUG] --- КОНЕЦ ВЫБОРА ВАЛЮТЫ ---\n")
        except Exception as e:
            print(f"[DEBUG] КРИТИЧЕСКАЯ ОШИБКА при выборе пункта валюты: {e}")
            raise

    @allure.step("Открыть секцию выбора иконки счета")
    def open_icon_selection(self):
        """Кликает по полю 'Иконка счета' для открытия панели выбора"""
        trigger = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.ICON_SECTION_TRIGGER))
        try:
            trigger.click()
            print("[DEBIT PAGE] Секция выбора иконки открыта.")
        except Exception:
            self.driver.execute_script("arguments[0].click();", trigger)
        time.sleep(0.5)

    @allure.step("Перейти на вкладку 'Банки'")
    def click_banks_tab(self):
        """Кликает по вкладке 'Банки' внутри модального окна/панели иконок"""
        tab = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.BANKS_TAB))
        try:
            tab.click()
            print("[DEBIT PAGE] Перешли на вкладку 'Банки'")
        except Exception:
            self.driver.execute_script("arguments[0].click();", tab)
        time.sleep(0.3)

    @allure.step("Выбрать первую доступную банковскую иконку")
    def select_first_bank_icon(self):
        """Находит и кликает по иконке на основе стабильного атрибута data-type='bank'"""
        icon = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.FIRST_BANK_ICON))
        try:
            icon.click()
            print("[DEBIT PAGE] Банковская иконка успешно выбрана.")
        except Exception:
            self.driver.execute_script("arguments[0].click();", icon)

    @allure.step("Выбрать самую первую иконку из стандартной секции 'Иконки'")
    def select_first_regular_icon(self):
        """Находит и кликает по первой иконке (лапке) в стандартной вкладке оформления"""
        icon = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.FIRST_REGULAR_ICON)
        )
        try:
            icon.click()
            print("[DEBIT PAGE] Выбрана первая стандартная иконка счета.")
        except Exception:
            self.driver.execute_script("arguments[0].click();", icon)
        time.sleep(0.3)

    @allure.step("Открыть секцию выбора цвета иконки")
    def open_color_selection(self):
        """Кликает по блоку 'Цвет иконки' для отображения палитры квадратов"""
        trigger = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.COLOR_SECTION_TRIGGER)
        )
        try:
            trigger.click()
            print("[DEBIT PAGE] Палитра цветов иконки успешно раскрыта.")
        except Exception:
            self.driver.execute_script("arguments[0].click();", trigger)
        time.sleep(0.5)

    @allure.step("Выбрать первый (серый) цвет из палитры")
    def select_first_color(self):
        """Кликает по первому доступному квадрату цвета на основе стабильного role='button'"""
        color_square = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.FIRST_COLOR_OPTION)
        )
        try:
            color_square.click()
            print("[DEBIT PAGE] Выбран первый цвет иконки (серый).")
        except Exception:
            self.driver.execute_script("arguments[0].click();", color_square)
        time.sleep(0.3)

    @allure.step("Кликнуть по кнопке 'Сохранить'")
    def click_save_button(self):
        btn = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.SAVE_BUTTON))
        try:
            btn.click()
            print("[DEBIT PAGE] Нажата кнопка 'Сохранить' обычным кликом")
        except Exception:
            print("[DEBIT PAGE] Обычный клик заблокирован, используем JavaScript-клик для 'Сохранить'...")
            self.driver.execute_script("arguments[0].click();", btn)

    def click_edit_account_in_dropdown(self):
        """Кликает по кнопке 'Настроить счет' в выпадающем меню счетов"""
        edit_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.BTN_EDIT_IN_DROPDOWN)
        )
        edit_btn.click()

    # === МЕТОДЫ ВАЛИДАЦИИ И ОШИБОК ===

    def is_too_long_error_visible(self) -> bool:
        try:
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(self.TOO_LONG_ERROR_MSG))
            return True
        except TimeoutException:
            return False

    def get_account_name_label_text(self) -> str:
        element = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(self.ACCOUNT_NAME_LABEL))
        return element.text

    def get_currency_label_text(self) -> str:
        element = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(self.CURRENCY_LABEL))
        return element.text

    def is_name_required_error_visible(self) -> bool:
        try:
            WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(self.NAME_REQUIRED_ERROR))
            return True
        except TimeoutException:
            return False

    def is_currency_required_error_visible(self) -> bool:
        try:
            WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(self.CURRENCY_REQUIRED_ERROR))
            return True
        except TimeoutException:
            return False

    # === ПРОВЕРКА СОЗДАННЫХ КАРТОЧЕК ===

    @allure.step("Дождаться создания счета и появления карточки '{name}'")
    def wait_until_account_created(self, name: str):
        print(f"[DEBIT PAGE] Ждем появления карточки с именем: {name}...")
        card_title_locator = (By.XPATH, f"//*[contains(normalize-space(.), '{name}')]")
        WebDriverWait(self.driver, 15).until(EC.visibility_of_element_located(card_title_locator))
        print(f"[DEBIT PAGE] Карточка '{name}' успешно появилась.")

    @allure.step("Проверить, что в карточке '{name}' отображается 'Дебетовый' и баланс '0,00 ₽'")
    def check_card_details(self, name: str):
        card_container_xpath = (
            f"//*[text()='{name}']/ancestor::div["
            f"contains(@class, 'Slide') or "
            f"contains(@class, 'Card') or "
            f"contains(@class, 'card') or "
            f"contains(@class, 'item')][1]"
        )
        try:
            card_container = self.driver.find_element(By.XPATH, card_container_xpath)
            print(f"[DEBIT PAGE] Родительский контейнер для карточки '{name}' успешно найден.")
            
            with allure.step("Проверить тип счета 'Дебетовый'"):
                card_type = card_container.find_element(By.XPATH, ".//*[text()='Дебетовый']")
                assert card_type.is_displayed(), f"В карточке '{name}' не найден тип 'Дебетовый'!"
            
            with allure.step("Проверить баланс '0,00 ₽'"):
                card_balance = card_container.find_element(By.XPATH, ".//*[contains(., '0,00')]")
                assert card_balance.is_displayed(), f"В карточке '{name}' не найден баланс '0,00'!"
            print(f"[DEBIT PAGE] Проверка содержимого карточки '{name}' — УСПЕШНО.")
        except NoSuchElementException as e:
            raise AssertionError(f"Не удалось найти контейнер карточки с именем '{name}' или элементы внутри неё! Ошибка: {e}")

    @allure.step("Проверить, что в карточке '{name}' отображается баланс '150,78 $', тип 'Дебетовый' и выбранная иконка с атрибутом alt")
    def check_card_with_icon_and_usd(self, name: str):
        """Глубокая проверка созданной карточки: проверяет тип, сумму, валюту $ и наличие иконки с alt"""
        card_container_xpath = f"//*[text()='{name}']/ancestor::div[contains(@class, 'Slide') or contains(@class, 'Card')][1]"
        try:
            card_container = self.driver.find_element(By.XPATH, card_container_xpath)
            print(f"[DEBIT PAGE] Контейнер для детальной проверки карточки '{name}' найден.")
            
            with allure.step("Проверить тип счета 'Дебетовый'"):
                card_type = card_container.find_element(By.XPATH, ".//*[text()='Дебетовый']")
                assert card_type.is_displayed(), f"В карточке '{name}' не найден тип 'Дебетовый'!"
            
            with allure.step("Проверить баланс '150,78' и знак валюты '$'"):
                card_text = card_container.text
                assert "150,78" in card_text, f"Сумма '150,78' не найдена в карточке! Текст: {card_text}"
                assert "$" in card_text, f"Значок валюты '$' не найден в карточке! Текст: {card_text}"
            
            with allure.step("Проверить наличие кастомной иконки на карточке и атрибут alt"):
                icon_xpath = f"//img[@alt='{name}']"
                icon_element = WebDriverWait(self.driver, 5).until(
                    EC.visibility_of_element_located((By.XPATH, icon_xpath))
                )
                alt_text = icon_element.get_attribute("alt")
                
                assert icon_element.is_displayed(), "Иконка оформления не отображается на карточке счета!"
                assert alt_text == name, f"Ошибка: Атрибут alt '{alt_text}' не совпадает с именем счета '{name}'!"
                print(f"[DEBIT PAGE] Иконка успешно отрисовалась! Её атрибут alt равен: '{alt_text}'")
                
            print(f"[DEBIT PAGE] Глубокая проверка карточки '{name}' пройдена успешно!")
        except Exception as e:
            raise AssertionError(f"Не удалось найти карточку '{name}' или обязательные элементы внутри неё! Ошибка: {e}")

    @allure.step("Проверить, что в карточке '{name}' отображается максимальный баланс и кастомная иконка")
    def check_card_with_huge_balance_and_icon(self, name: str):
        """Глубокая проверка созданной карточки: верифицирует тип, максимальную сумму баланса и иконку"""
        card_container_xpath = f"//p[contains(text(), '{name}')]/ancestor::div[contains(@class, 'AccountCardstyled__Root')][1]"
        try:
            card_container = self.driver.find_element(By.XPATH, card_container_xpath)
            print(f"[DEBIT PAGE] Контейнер для проверки сверхбольшого баланса карточки '{name}' найден.")
            
            # 1. Проверяем тип счета
            with allure.step("Проверить тип счета 'Дебетовый'"):
                card_type = card_container.find_element(By.XPATH, ".//*[text()='Дебетовый']")
                assert card_type.is_displayed(), f"В карточке '{name}' не найден тип 'Дебетовый'!"
            
            # 2. Проверяем точную сумму баланса
            with allure.step("Проверить точную сумму баланса '999999999999,99₽'"):
                cleaned_text = "".join(card_container.text.split())
                print(f"[DEBIT PAGE] Текст карточки после полной очистки: '{cleaned_text}'")
                
                assert "999999999999,99" in cleaned_text, f"Сверхбольшая сумма баланса не найдена в очищенном тексте карточки! Текст: {cleaned_text}"
                assert "₽" in cleaned_text, f"Значок валюты '₽' не найден в очищенном тексте карточки! Текст: {cleaned_text}"
            
            # 3. НАДЕЖНАЯ ПРОВЕРКА ИКОНКИ (ждем отрисовку именно видимого графического элемента)
            with allure.step("Проверить наличие отрисованной иконки на карточке"):
                icon_relative_xpath = (
                    ".//img | .//svg | .//i | "
                    ".//*[contains(@class, 'icon') or contains(@class, 'Icon') or contains(@class, 'Image') or contains(@class, 'IconWrapper')]"
                )
                
                def find_visible_icon(d):
                    elements = card_container.find_elements(By.XPATH, icon_relative_xpath)
                    for el in elements:
                        if el.is_displayed() or el.tag_name in ['img', 'svg']:
                            return el
                    return None

                icon_element = WebDriverWait(self.driver, 5).until(find_visible_icon)
                assert icon_element is not None, "Выбранная иконка оформления не отображается внутри карточки счета!"
                print("[DEBIT PAGE] Проверка стандартной иконки и огромного баланса на карточке пройдена успешно!")
                
        except Exception as e:
            raise AssertionError(f"Не удалось найти карточку '{name}' или обязательные элементы внутри неё! Ошибка: {e}")

    @allure.step("Нажать на иконку 'Все счета'")
    def click_all_accounts_button(self):
        """Кликает по кнопке с иконкой кошелька для перехода в боковую панель/окно 'Все счета'"""
        btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.ALL_ACCOUNTS_BTN)
        )
        try:
            btn.click()
            print("[DEBIT PAGE] Нажата иконка 'Все счета'.")
        except Exception:
            self.driver.execute_script("arguments[0].click();", btn)
        time.sleep(1)

    @allure.step("Проверить созданный аккаунт '{name}' внутри списка 'Все счета'")
    def check_account_in_all_accounts_modal(self, name: str):
        """Проверяет наличие строки созданного счета, его триллионный баланс и плашку иконки"""
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.ALL_ACCOUNTS_HEADER)
        )
        print("[DEBIT PAGE] Модальное окно 'Все счета' успешно открыто.")
        
        try:
            # 1. Находим корневой контейнер карточки счета в списке
            card_container = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(self.MODAL_ACCOUNT_CARD_BY_NAME(name))
            )
            
            # 2. Проверяем баланс внутри найденой карточки
            with allure.step("Проверить баланс счета в списке 'Все счета'"):
                balance_element = card_container.find_element(
                    By.XPATH, ".//div[contains(@class, 'BalanceWrapper')]"
                )
                cleaned_balance_text = "".join(balance_element.text.split())
                print(f"[DEBIT PAGE] Текст баланса в модальном окне после очистки: '{cleaned_balance_text}'")
                
                assert "999999999999,99" in cleaned_balance_text, f"Ошибка: Сумма баланса не найдена! Текст: {cleaned_balance_text}"
                assert "₽" in cleaned_balance_text, "Ошибка: Значок валюты '₽' отсутствует!"

            # 3. Проверяем плашку с иконкой справа (BalanceCard__Root)
            with allure.step("Проверить отображение иконки у счета в списке"):
                icon_element = card_container.find_element(
                    By.XPATH, ".//div[contains(@class, 'BalanceCard__Root')]"
                )
                assert icon_element.is_displayed(), f"Иконка оформления для счета '{name}' не отображается в списке!"
                print(f"[DEBIT PAGE] УСПЕХ! Строка счета '{name}' содержит плашку иконки.")

        except Exception as e:
            raise AssertionError(f"Не удалось выполнить проверку счета '{name}' в окне 'Все счета'! Ошибка: {e}")

    @allure.step("Убедиться, что счёт с новым именем '{name}' отображается в списке 'Все счета'")
    def assert_account_name_visible_in_modal(self, name: str):
        """Проверяет, что элемент с новым названием счёта присутствует на экране внутри модального окна"""
        name_xpath = f"//div[contains(@class, 'TitleWrapper')]//*[text()='{name}'] | //*[contains(@class, 'AccountListCard')]//*[text()='{name}']"
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, name_xpath))
            )
            assert element.is_displayed(), f"Новое имя счёта '{name}' не отображается в модальном окне!"
            print(f"[DEBIT PAGE] Переименованный счёт '{name}' успешно найден в списке 'Все счета'.")
        except TimeoutException:
            raise AssertionError(f"Ошибка: Новое имя счёта '{name}' не появилось в окне 'Все счета' за 10 секунд!")

    # === МЕТОДЫ ДЛЯ СЦЕНАРИЯ УДАЛЕНИЯ ===

    @allure.step("Нажать на 3 точки у карточки счета '{name}'")
    def click_three_dots_for_account(self, name: str):
        """Находит и открывает меню 3 точек конкретной карточки по её названию"""
        self.close_promo_popup_if_present()
        
        # 1. Находим карточку в DOM
        card = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.ACCOUNT_CARD_BY_NAME(name))
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", card)
        
        # 2. Находим 3 точки именно этой карточки по aria-haspopup='dialog'
        btn = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.THREE_DOTS_BY_NAME(name))
        )
        
        try:
            btn.click()
        except Exception:
            self.driver.execute_script("""
                var el = arguments[0];
                el.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true, view: window}));
            """, btn)
            
        print(f"[DEBIT PAGE] Нажаты 3 точки строго у карточки '{name}'")
        time.sleep(0.5)

    @allure.step("Выбрать пункт 'Удалить счет' в раскрывающемся списке")
    def click_delete_account_in_dropdown(self):
        item = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.DELETE_DROPDOWN_ITEM))
        try:
            item.click()
            print("[DEBIT PAGE] В меню выбран пункт 'Удалить счет'")
        except Exception:
            self.driver.execute_script("arguments[0].click();", item)

    @allure.step("В первом модальном окне подтверждения нажать 'Удалить счет'")
    def click_confirm_delete_first_stage(self):
        confirm_btn = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.CONFIRM_DELETE_FIRST_BTN))
        try:
            confirm_btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", confirm_btn)
        print("[DEBIT PAGE] В первом модальном окне нажата кнопка 'Удалить счет'")
        time.sleep(0.5)

    @allure.step("Выбрать оба чекбокса (согласия) во втором модальном окне")
    def tick_both_delete_checkboxes(self):
        cb1 = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.DELETE_CHECKBOX_1))
        cb2 = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.DELETE_CHECKBOX_2))
        
        try:
            cb1.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", cb1)
        print("[DEBIT PAGE] Выбран первый чекбокс согласия.")
        
        try:
            cb2.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", cb2)
        print("[DEBIT PAGE] Выбран второй чекбокс согласия.")
        
        time.sleep(0.3)

    @allure.step("В финальном окне нажать кнопку 'Удалить счет'")
    def click_confirm_delete_final_stage(self):
        btn = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.CONFIRM_DELETE_FINAL_BTN)
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        
        try:
            btn.click()
        except Exception:
            pass
            
        self.driver.execute_script("arguments[0].click();", btn)
        print("[DEBIT PAGE] Финальная кнопка 'Удалить счет' успешно нажата.")
        time.sleep(1)

    @allure.step("Убедиться, что счет '{name}' полностью исчез с экрана")
    def assert_account_is_deleted(self, name: str):
        time.sleep(1.5)
        card_locator = (By.XPATH, f"//*[text()='{name}']")
        is_invisible = WebDriverWait(self.driver, 10).until(EC.invisibility_of_element_located(card_locator))
        assert is_invisible, f"Ошибка: Счет '{name}' всё еще отображается на странице после удаления!"
        print(f"[DEBIT PAGE] Проверка успешна: Счет '{name}' полностью удален с экрана.")

    @allure.step("Выполнить визуальную проверку страницы по скриншоту-эталону '{baseline_name}'")
    def verify_visual_screenshot(self, baseline_name: str):
        """
        Делает скриншот страницы и сравнивает его с эталоном пиксель-в-пиксель.
        Если эталона нет — создает его автоматически.
        """
        base_dir = "screenshots"
        baseline_path = os.path.join(base_dir, "baselines", f"{baseline_name}.png")
        actual_path = os.path.join(base_dir, "actual", f"{baseline_name}_actual.png")
        diff_path = os.path.join(base_dir, "diff", f"{baseline_name}_diff.png")
        
        os.makedirs(os.path.join(base_dir, "baselines"), exist_ok=True)
        os.makedirs(os.path.join(base_dir, "actual"), exist_ok=True)
        os.makedirs(os.path.join(base_dir, "diff"), exist_ok=True)
        
        time.sleep(1)
        
        self.driver.save_screenshot(actual_path)
        allure.attach.file(actual_path, name="Фактический скриншот (Actual)", attachment_type=allure.attachment_type.PNG)
        
        if not os.path.exists(baseline_path):
            self.driver.save_screenshot(baseline_path)
            allure.attach.file(baseline_path, name="Создан новый эталон (Baseline)", attachment_type=allure.attachment_type.PNG)
            print(f"\n[VISUAL] Создан новый скриншот-эталон: {baseline_path}")
            print("[VISUAL] При следующем прогоне этот тест будет сравниваться с ним.")
            return

        img_baseline = Image.open(baseline_path).convert('RGB')
        img_actual = Image.open(actual_path).convert('RGB')
        
        diff = ImageChops.difference(img_baseline, img_actual)
        
        if diff.getbbox():
            diff.save(diff_path)
            allure.attach.file(baseline_path, name="Эталонный скриншот (Baseline)", attachment_type=allure.attachment_type.PNG)
            allure.attach.file(diff_path, name="Разница в верстке (Diff)", attachment_type=allure.attachment_type.PNG)
            
            raise AssertionError(
                f"Визуальная проверка провалена! Обнаружены расхождения с фото-эталоном '{baseline_name}'. "
                f"Посмотрите разницу (Diff) в отчете Allure."
            )
        else:
            print(f"[VISUAL] Успех! Страница полностью соответствует скриншот-эталону '{baseline_name}'.")

    def close_promo_popup_if_present(self):
        """Безопасное закрытие промо-окна (ищет крестик строго рядом с рекламным текстом)"""
        try:
            # Ищем кнопку закрытия только в тех контейнерах, где есть слова из промо-баннера
            promo_xpath = (
                "//*[contains(text(), 'ПОДАРОК') or contains(text(), 'Пройдите тест') or contains(text(), '1 минуту')]"
                "/ancestor::div[position()<=5]//*[self::button or name()='svg' or contains(@class, 'close')]"
            )
            close_buttons = self.driver.find_elements(By.XPATH, promo_xpath)
            for btn in close_buttons:
                try:
                    if btn.is_displayed():
                        self.driver.execute_script("arguments[0].click();", btn)
                        print("[DEBIT PAGE] Рекламное промо-окно успешно закрыто.")
                        time.sleep(0.5)
                        break
                except Exception:
                    continue
        except Exception:
            pass