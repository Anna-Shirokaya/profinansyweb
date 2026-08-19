# === FILE: pages/auth_pages/registration_page.py ===
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class RegistrationPage:
    def __init__(self, driver):
        self.driver = driver
        
        # ЛОКАТОРЫ
        # Используем NAME вместо XPATH по placeholder для максимальной точности
        self.INPUT_EMAIL = (By.NAME, "email") 
        self.CHECKBOX_POLICY = (By.XPATH, "//input[@name='policy_agreement']") 
        self.CHECKBOX_PROMO = (By.XPATH, "//input[@name='promo_agreement']")   
        self.BTN_ONE_STEP_LEFT = (By.XPATH, "//button[contains(text(), 'Остался один шаг')]")
        self.ERROR_MESSAGE_EMAIL = (By.XPATH, "//*[contains(text(), 'Некорректный e-mail')]")
        
        # Локаторы куки и промо (как на WelcomePage)
        self.COOKIE_ACCEPT_BUTTON = (By.XPATH, "//*[text()='Понятно']")
        self.PROMO_CLOSE_BUTTON = (By.XPATH, "//button[contains(@class, 'close')] | //div[contains(@class, 'close')]")

    def open_directly(self):
        """Прямой переход по ссылке из тест-кейсов с закрытием поп-апов"""
        self.driver.get("https://profinansy.ru/login/registration")
        self.close_cookie_banner_if_exists()
        self.close_promo_modal_if_exists()

    def close_cookie_banner_if_exists(self):
        try:
            cookie_btn = WebDriverWait(self.driver, 4).until(
                EC.element_to_be_clickable(self.COOKIE_ACCEPT_BUTTON)
            )
            cookie_btn.click()
        except TimeoutException:
            pass

    def close_promo_modal_if_exists(self):
        try:
            close_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(self.PROMO_CLOSE_BUTTON)
            )
            close_btn.click()
        except (TimeoutException, NoSuchElementException):
            pass

    def enter_email(self, email):
        """Ожидает появления поля ввода, кликает по нему через JS и вводит email"""
        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.INPUT_EMAIL)
        )
        self.driver.execute_script("arguments[0].click();", element) # Клик через JavaScript
        element.clear()
        element.send_keys(email)

    def select_all_checkboxes(self):
        """Прокликивает чек-боксы согласий"""
        policy_checkbox = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.CHECKBOX_POLICY)
        )
        policy_checkbox.click()
        
        promo_checkbox = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.CHECKBOX_PROMO)
        )
        promo_checkbox.click()

    def is_one_step_button_enabled(self):
        """Проверяет, активна ли кнопка 'Остался один шаг'"""
        btn = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.BTN_ONE_STEP_LEFT)
        )
        return btn.is_enabled()

    def click_one_step_left(self):
        """Кликает по кнопке 'Остался один шаг'"""
        btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.BTN_ONE_STEP_LEFT)
        )
        btn.click()

    def get_email_error_text(self):
        """Получает текст ошибки валидации email"""
        error_el = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.ERROR_MESSAGE_EMAIL)
        )
        return error_el.text

# === FILE: pages/auth_pages/welcome_page.py ===
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException 

class WelcomePage:
    def __init__(self, driver):
        self.driver = driver
        self.url = f"{driver.base_url}/welcome"
        
        # ЛОКАТОРЫ
        self.LOGIN_BUTTON = (By.XPATH, "//*[text()='Вход']")
        
        # НОВЫЙ ЛОКАТОР: Кнопка регистрации (согласно тест-кейсу WAL-T301)
        self.REGISTER_BUTTON = (By.XPATH, "//*[text()='Регистрация']")
        
        # Локаторы всплывающих окон
        self.COOKIE_ACCEPT_BUTTON = (By.XPATH, "//*[text()='Понятно']")
        self.PROMO_CLOSE_BUTTON = (By.XPATH, "//button[contains(@class, 'close')] | //div[contains(@class, 'close')]")


    def open(self):
        """Метод для открытия страницы"""
        self.driver.get(self.url)
        # После открытия проверяем и закрываем куки и промо-модалку
        self.close_cookie_banner_if_exists()
        self.close_promo_modal_if_exists()


    def close_cookie_banner_if_exists(self):
        """Метод автоматически закрывает баннер куки, если он есть на экране"""
        try:
            # Ждем появления кнопки куки максимум 4 секунды
            cookie_btn = WebDriverWait(self.driver, 4).until(
                EC.element_to_be_clickable(self.COOKIE_ACCEPT_BUTTON)
            )
            cookie_btn.click()
            print("\n[PAGE] Баннер куки успешно закрыт.")
        except TimeoutException:
            # Если баннер не появился, тест не упадет
            print("\n[PAGE] Баннер куки не появился, продолжаем тест.")


    def close_promo_modal_if_exists(self):
        """Метод проверяет наличие промо-модального окна и закрывает его по крестику"""
        try:
            # Ждем появления крестика модального окна максимум 5 секунд
            close_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(self.PROMO_CLOSE_BUTTON)
            )
            close_btn.click()
            print("\n[PAGE] Промо-модальное окно успешно закрыто.")
        except TimeoutException:
            print("\n[PAGE] Промо-модальное окно не появилось, продолжаем тест.")
        except NoSuchElementException:
             print("\n[PAGE] Промо-модальное окно не найдено, продолжаем тест.")


    def click_login_button(self):
        """Метод для клика по кнопке Вход с защитой от перекрытия"""
        # Ждем, пока кнопка станет видимой
        login_btn = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.LOGIN_BUTTON)
        )
        
        try:
            # 1. Пробуем кликнуть как обычный пользователь
            login_btn.click()
        except Exception:
            # 2. Если клик перехвачен исчезающей анимацией, кликаем через JavaScript
            print("\n[PAGE] Обычный клик перехвачен, используем JavaScript-клик...")
            self.driver.execute_script("arguments[0].click();", login_btn)

    def click_register_button(self):
        """Метод для клика по кнопке Регистрация с защитой от перекрытия"""
        # Ждем, пока кнопка станет видимой
        register_btn = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.REGISTER_BUTTON)
        )
        
        try:
            # 1. Пробуем кликнуть как обычный пользователь
            register_btn.click()
        except Exception:
            # 2. Если клик перехвачен исчезающей анимацией, кликаем через JavaScript
            print("\n[PAGE] Обычный клик перехвачен, используем JavaScript-клик для кнопки Регистрация...")
            self.driver.execute_script("arguments[0].click();", register_btn)

# === FILE: pages/auth_pages/login_page.py===
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LoginPage:
    def __init__(self, driver):
        self.driver = driver

        # ЛОКАТОРЫ
        # Поле Email ищем по атрибуту placeholder или типу поля
        self.EMAIL_INPUT = (By.XPATH, "//input[@placeholder='E-mail' or @type='email']")
        
        # Поле Пароль ищем аналогично
        self.PASSWORD_INPUT = (By.XPATH, "//input[@placeholder='Введите пароль' or @type='password']")
        
        # Кнопка "Войти" — строго ищем тег кнопки (button), внутри которого текст "Войти"
        # Это защитит нас от случайного клика по заголовку страницы
        self.SUBMIT_BUTTON = (By.XPATH, "//button[contains(., 'Войти')] | //input[@type='submit']")

    def enter_email(self, email: str):
        """Очищает поле и вводит Email с ожиданием появления элемента"""
        email_field = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.EMAIL_INPUT)
        )
        email_field.clear()
        email_field.send_keys(email)
        print(f"[LOGIN PAGE] Введен email: {email}")

    def enter_password(self, password: str):
        """Очищает поле и вводит пароль"""
        password_field = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.PASSWORD_INPUT)
        )
        password_field.clear()
        password_field.send_keys(password)
        print("[LOGIN PAGE] Введен пароль.")

    def click_submit_button(self):
        """Кликает по фиолетовой кнопке 'Войти' с защитой от перекрытия анимациями"""
        submit_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.SUBMIT_BUTTON)
        )
        
        try:
            # 1. Пробуем кликнуть стандартным способом Selenium
            submit_btn.click()
            print("[LOGIN PAGE] Нажата фиотеловая кнопка 'Войти' обычным кликом.")
        except Exception:
            # 2. Если анимация React перекрыла кнопку, бьем через JavaScript напрямую в DOM
            print("\n[LOGIN PAGE] Обычный клик перехвачен анимацией подложки, используем JavaScript-клик...")
            self.driver.execute_script("arguments[0].click();", submit_btn)

# === FILE:pages/dashboard_pages/dashboard_page.py===
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class DashboardPage:
    def __init__(self, driver):
        self.driver = driver

        # ЛОКАТОРЫ
        self.MY_MONEY_HEADER = (By.XPATH, "//*[text()='Мои деньги']")
        
        self.POPUP_CLOSE_BUTTON = (By.XPATH, (
            "//button[contains(@class, 'close')] | //div[contains(@class, 'close')] | "
            "//*[contains(@class, 'Close')] | //button[@aria-label='Close']"
        ))

        self.BUDGET_MENU_BUTTON = (By.XPATH, "//nav//a[contains(., 'Бюджет')] | //*[text()='Бюджет']")
        
        # Упрощаем локатор: просто ищем текст "Счета". Фильтрацию по видимости сделаем в коде ниже!
        self.ACCOUNTS_TEXT_ELEMENTS = (By.XPATH, "//*[text()='Счета']")

    def close_popup_if_exists(self):
        try:
            close_btn = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable(self.POPUP_CLOSE_BUTTON)
            )
            close_btn.click()
            time.sleep(1)
        except Exception:
            pass

    def is_my_money_header_visible(self) -> bool:
        self.close_popup_if_exists()
        try:
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(self.MY_MONEY_HEADER)
            )
            return True
        except Exception:
            return False

    def open_accounts_section(self):
        """Переходит в раздел Счета через верхнее меню Бюджет"""
        # 1. Ждем, пока кнопка "Бюджет" станет доступной для клика
        budget_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.BUDGET_MENU_BUTTON)
        )
        
        # Добавляем try-except защиту от летящих анимаций React на QA стендах
        try:
            budget_btn.click()
            print("[DASHBOARD] Кликнули по меню 'Бюджет' обычным кликом")
        except Exception:
            print("[DASHBOARD] Обычный клик по 'Бюджет' перехвачен, используем JavaScript-клик...")
            self.driver.execute_script("arguments[0].click();", budget_btn)

        # 2. Ждем, пока на странице появится хотя бы один видимый элемент с текстом "Счета"
        visible_elements = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_any_elements_located(self.ACCOUNTS_TEXT_ELEMENTS)
        )
        
        # 3. Выбираем именно тот, который отображается на экране
        target_card = None
        for elem in visible_elements:
            if elem.is_displayed():
                target_card = elem
                break
                
        assert target_card is not None, "Ошибка: На экране не найдено ни одного видимого элемента 'Счета'!"

        # 4. Кликаем по активной карточке "Счета"
        try:
            target_card.click()
            print("[DASHBOARD] Кликнули по активному меню 'Счета' обычным кликом")
        except Exception:
            print("[DASHBOARD] Обычный клик перехвачен, используем JavaScript-клик для 'Счета'...")
            self.driver.execute_script("arguments[0].click();", target_card)


# === FILE: pages/debit_pages/accounts_main_page.py===
import time
import allure
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from PIL import Image, ImageChops

class AccountsMainPage:
    def __init__(self, driver):
        self.driver = driver
        
        # ЛОКАТОРЫ СТРАНИЦЫ И ПУСТОГО СОСТОЯНИЯ
        self.EMPTY_STATE_TITLE = (By.XPATH, "//*[text()='Здесь пока ничего нет']")
        self.EMPTY_STATE_DESC = (By.XPATH, "//*[contains(text(), 'Чтобы начать пользоваться бюджетом')]")
        self.CREATE_ACCOUNT_BTN = (By.XPATH, "//button[contains(., 'Создать счёт')]")
        
        # ЛОКАТОРЫ ФОРМЫ СОЗДАНИЯ СЧЕТА
        self.DEBIT_TYPE_CARD = (By.XPATH, "//*[text()='Дебетовый']")
        self.CONTINUE_BUTTON = (By.XPATH, "//button[contains(., 'Продолжить')] | //*[text()='Продолжить']")
        self.ACCOUNT_NAME_INPUT = (By.XPATH, "//input[@placeholder='Введите название']")
        self.BALANCE_INPUT = (By.XPATH, "//*[contains(text(), 'Баланс')]/following::input[1]")
        self.CURRENCY_SELECT_TRIGGER = (By.XPATH, "//input[@placeholder='Выберите валюту из списка']")
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
        # ЛОКАТОРЫ ДЛЯ СЕКЦИИ ОБЫЧНЫХ ИКОНОК И ЦВЕТА (ПО image_af0cfa.png и image_af105d.png)
        # Находит первую иконку-кнопку строго после заголовка "Иконка счета", исключая вкладку банков
        self.FIRST_REGULAR_ICON = (By.XPATH, "//*[contains(text(), 'Иконка счета')]/following::span[@role='button' and not(@data-type='bank')][1]")
        # Находит плашку раскрытия секции "Цвет иконки"
        self.COLOR_SECTION_TRIGGER = (By.XPATH, "//*[text()='Цвет иконки']/ancestor::div[1] | //*[contains(text(), 'Цвет иконки')]")
        # Находит самый первый цветовой квадрат-кнопку строго после заголовка "Цвет иконки"
        self.FIRST_COLOR_OPTION = (By.XPATH, "//*[contains(text(), 'Цвет иконки')]/following::span[@role='button'][1]")

        # ЛОКАТОРЫ ДЛЯ ОКНА "ВСЕ СЧЕТА" (ПО image_afde9d.png)
        # Находит первую кнопку в блоке кнопок карусели (иконка кошелька/карточек)
        self.ALL_ACCOUNTS_BTN = (By.XPATH, "//div[contains(@class, 'ButtonsBlock')]//button[1]")
        self.ALL_ACCOUNTS_HEADER = (By.XPATH, "//*[text()='Все счета']")
        # ЛОКАТОР ДЛЯ КНОПКИ НАСТРОЙКИ СЧЕТА В ПАЛЕТКЕ СЧЕТА
        self.BTN_EDIT_IN_DROPDOWN = (By.XPATH, "//span[text()='Настроить счет']")

    def is_page_loaded(self) -> bool:
        """Проверяет загрузку страницы счетов"""
        time.sleep(1)
        current_url = self.driver.current_url
        print(f"[DEBIT PAGE] Текущий URL страницы: {current_url}")
        return "budget" in current_url or "account" in current_url

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
        btn = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.CREATE_ACCOUNT_BTN))
        btn.click()
        print("[DEBIT PAGE] Нажата кнопка 'Создать счёт +'")

    @allure.step("Выбрать тип счёта 'Дебетовый'")
    def select_debit_account_type(self):
        card = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.DEBIT_TYPE_CARD))
        try:
            card.click()
            print("[DEBIT PAGE] Выбран тип счёта: Дебетовый (обычный клик)")
        except Exception:
            print("[DEBIT PAGE] Обычный клик перехвачен, используем JavaScript-клик...")
            self.driver.execute_script("arguments[0].click();", card)

    @allure.step("Кликнуть 'Продолжить', если кнопка отображается")
    def click_continue_if_exists(self):
        try:
            btn = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(self.CONTINUE_BUTTON))
            btn.click()
            print("[DEBIT PAGE] Нажата кнопка 'Продолжить'")
        except TimeoutException:
            print("[DEBIT PAGE] Кнопка 'Продолжить' не потребовалась")

    @allure.step("Ввести название счёта: {name_text}")
    def enter_account_name(self, name_text: str):
        input_field = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.ACCOUNT_NAME_INPUT))
        input_field.clear()
        input_field.send_keys(name_text)
        print(f"[DEBIT PAGE] Введено название счёта длиной {len(name_text)} символов")

    @allure.step("Ввести начальный баланс: {balance_text}")
    def enter_balance(self, balance_text: str):
        """Вводит сумму в поле 'Баланс' с предварительной очисткой через горячие клавиши"""
        input_field = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.BALANCE_INPUT))
        input_field.click()
        
        from selenium.webdriver.common.keys import Keys
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
        """Универсальный метод: открывает селект и выбирает валюту по её точному названию"""
        currency_trigger = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.CURRENCY_SELECT_TRIGGER))
        try:
            currency_trigger.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", currency_trigger)
            
        time.sleep(0.5)
        
        option_xpath = f"//div[contains(@class, 'Select-dropdown')]//li[contains(., '{currency_name}')]"
        option = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, option_xpath)))
        try:
            option.click()
            print(f"[DEBIT PAGE] Выбрана валюта: '{currency_name}'")
        except Exception:
            self.driver.execute_script("arguments[0].click();", option)

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
            EC.element_to_be_clickable(self.BTN_EDIT_IN_DROPDOWN) # Обращаемся через self.
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
        card_title_locator = (By.XPATH, f"//*[text()='{name}']")
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
            # Находим контейнер именно этой карточки
            card_container = self.driver.find_element(By.XPATH, card_container_xpath)
            print(f"[DEBIT PAGE] Контейнер для детальной проверки карточки '{name}' найден.")
            
            # 1. Проверяем тип счета
            with allure.step("Проверить тип счета 'Дебетовый'"):
                card_type = card_container.find_element(By.XPATH, ".//*[text()='Дебетовый']")
                assert card_type.is_displayed(), f"В карточке '{name}' не найден тип 'Дебетовый'!"
            
            # 2. Проверяем баланс и валюту во всем тексте карточки
            with allure.step("Проверить баланс '150,78' и знак валюты '$'"):
                card_text = card_container.text
                assert "150,78" in card_text, f"Сумма '150,78' не найдена в карточке! Текст: {card_text}"
                assert "$" in card_text, f"Значок валюты '$' не найден в карточке! Текст: {card_text}"
            
            # 3. УЛЬТРА-НАДЕЖНОЕ ОЖИДАНИЕ ИКОНКИ ПО АТРИБУТУ ALT
            with allure.step("Проверить наличие кастомной иконки на карточке и атрибут alt"):
                # Ищем картинку глобально по её уникальному alt, давая React время на отрисовку
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
    # === МЕТОДЫ ДЛЯ СЦЕНАРИЯ УДАЛЕНИЯ ===

    @allure.step("Нажать на 3 точки у карточки счета '{name}'")
    def click_three_dots_for_account(self, name: str):
        """Находит кнопку 3 точек внутри конкретной карточки счета по её имени"""
        # ИСПРАВЛЕНО: Убрали contains(@class, 'item'), чтобы поиск не застревал во внутренних текстовых div.
        # Теперь мы поднимаемся строго до главного контейнера слайда/карточки, где кнопка доступна.
        three_dots_xpath = (
            f"//*[text()='{name}']/ancestor::div[contains(@class, 'Slide') or contains(@class, 'Card')][1]"
            f"//button[contains(@class, 'ActionButton') or @aria-haspopup='dialog']"
        )
        btn = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, three_dots_xpath)))
        try:
            btn.click()
            print(f"[DEBIT PAGE] Нажаты 3 точки для счета '{name}'")
        except Exception:
            print("[DEBIT PAGE] Обычный клик перехвачен, активируем через JavaScript...")
            self.driver.execute_script("arguments[0].click();", btn)
            
    @allure.step("Выбрать пункт 'Удалить счет' в раскрывающемся списке")
    def click_delete_account_in_dropdown(self):
        delete_dropdown_item = (By.XPATH, "//button[@class='removeBtn'] | //*[text()='Удалить счет']")
        item = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(delete_dropdown_item))
        try:
            item.click()
            print("[DEBIT PAGE] В меню выбран пункт 'Удалить счет'")
        except Exception:
            self.driver.execute_script("arguments[0].click();", item)

    @allure.step("В первом модальном окне подтверждения нажать 'Удалить счет'")
    def click_confirm_delete_first_stage(self):
        confirm_btn = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Удалить счет')]")))
        confirm_btn.click()
        print("[DEBIT PAGE] В первом модальном окне нажата кнопка 'Удалить счет'")
        time.sleep(0.5)

    @allure.step("Выбрать оба чекбокса (согласия) во втором модальном окне")
    def tick_both_delete_checkboxes(self):
        checkbox_1_xpath = "//*[contains(text(), 'Я понимаю, что удаление счета')]"
        checkbox_2_xpath = "//*[contains(text(), 'Я осознаю, что мое решение')]"
        cb1 = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, checkbox_1_xpath)))
        cb2 = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, checkbox_2_xpath)))
        cb1.click()
        print("[DEBIT PAGE] Выбран первый чекбокс согласия.")
        cb2.click()
        print("[DEBIT PAGE] Выбран второй чекбокс согласия.")
        time.sleep(0.3)

    @allure.step("В финальном окне нажать кнопку 'Удалить счет'")
    def click_confirm_delete_final_stage(self):
        final_btn = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Удалить счет')]")))
        try:
            final_btn.click()
            print("[DEBIT PAGE] Финальная кнопка 'Удалить счет' успешно нажата.")
        except Exception:
            self.driver.execute_script("arguments[0].click();", final_btn)

    @allure.step("Убедиться, что счет '{name}' полностью исчез с экрана")
    def assert_account_is_deleted(self, name: str):
        time.sleep(1.5)
        card_locator = (By.XPATH, f"//*[text()='{name}']")
        is_invisible = WebDriverWait(self.driver, 10).until(EC.invisibility_of_element_located(card_locator))
        assert is_invisible, f"Ошибка: Счет '{name}' всё еще отображается на странице после удаления!"
        print(f"[DEBIT PAGE] Проверка успешна: Счет '{name}' полностью удален с экрана.")

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

    @allure.step("Проверить, что в карточке '{name}' отображается максимальный баланс и кастомная иконка")
    def check_card_with_huge_balance_and_icon(self, name: str):
        """Глубокая проверка созданной карточки: верифицирует тип, максимальную сумму баланса и иконку"""
        # Нацеливаемся строго на родительский AccountCardstyled__Container (содержит слово Card)
        card_container_xpath = f"//*[text()='{name}']/ancestor::div[contains(@class, 'Card') or contains(@class, 'Container')][1]"
        try:
            # Находим контейнер именно этой карточки
            card_container = self.driver.find_element(By.XPATH, card_container_xpath)
            print(f"[DEBIT PAGE] Контейнер для проверки сверхбольшого баланса карточки '{name}' найден.")
            
            # 1. Проверяем тип счета
            with allure.step("Проверить тип счета 'Дебетовый'"):
                card_type = card_container.find_element(By.XPATH, ".//*[text()='Дебетовый']")
                assert card_type.is_displayed(), f"В карточке '{name}' не найден тип 'Дебетовый'!"
            
            # 2. ЖЕЛЕЗНАЯ ПРОВЕРКА БАЛАНСА ПО ТВОЕМУ СКРИНШОТУ:
            with allure.step("Проверить точную сумму баланса '999999999999,99₽'"):
                # .split() без аргументов склеит "999 999 999 999" + "," + "99" + "₽" 
                # из любых вложенных тегов <p> и <span>, убирая все переносы и пробелы!
                cleaned_text = "".join(card_container.text.split())
                print(f"[DEBIT PAGE] Текст карточки после полной очистки: '{cleaned_text}'")
                
                # Проверяем точное совпадение очищенной суммы и знака рубля
                assert "999999999999,99" in cleaned_text, f"Сверхбольшая сумма баланса не найдена в очищенном тексте карточки! Текст: {cleaned_text}"
                assert "₽" in cleaned_text, f"Значок валюты '₽' не найден в очищенном тексте карточки! Текст: {cleaned_text}"
            
            # 3. УЛЬТРА-НАДЕЖНОЕ ОЖИДАНИЕ ИКОНКИ (Защита от задержки рендеринга React)
            with allure.step("Проверить наличие отрисованной иконки на карточке"):
                # Ищем строго внутри контейнера карточки (.//) любой графический элемент: 
                # тег img, svg, или любой span/div, содержащий в классе упоминание Icon или Image
                icon_relative_xpath = (
                    ".//img | .//svg | .//i | "
                    ".//*[contains(@class, 'icon') or contains(@class, 'Icon') or contains(@class, 'Image') or contains(@class, 'IconWrapper')]"
                )
                
                # Даем React до 5 секунд на отрисовку графического элемента лапки
                icon_element = WebDriverWait(self.driver, 5).until(
                    lambda d: card_container.find_element(By.XPATH, icon_relative_xpath)
                )
                
                assert icon_element.is_displayed(), "Выбранная иконка оформления не отображается внутри карточки счета!"
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
        # Даем секунду на плавную анимацию открытия шторки/окна
        time.sleep(1)

    @allure.step("Проверить созданный аккаунт '{name}' внутри списка 'Все счета'")
    def check_account_in_all_accounts_modal(self, name: str):
        """Проверяет наличие строки созданного счета, его триллионный баланс и кастомную иконку с alt"""
        # 1. Проверяем, что окно "Все счета" успешно открылось
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.ALL_ACCOUNTS_HEADER)
        )
        print("[DEBIT PAGE] Модальное окно 'Все счета' успешно открыто.")
        
        try:
            # 2. ЖЕЛЕЗНАЯ ПРОВЕРКА БАЛАНСА ПО ТВОЕМУ НОВОМУ СКРИНШОТУ:
            # Шагаем через following-sibling строго от заголовка к соседнему блоку баланса
            balance_xpath = (
                f"//*[contains(text(), '{name}')]/"
                f"ancestor::div[contains(@class, 'TitleWrapper')]/"
                f"following-sibling::div[contains(@class, 'BalanceWrapper')]//p"
            )
            
            with allure.step("Проверить баланс счета в списке 'Все счета'"):
                balance_element = WebDriverWait(self.driver, 5).until(
                    EC.visibility_of_element_located((By.XPATH, balance_xpath))
                )
                
                # Очищаем от всех пробелов и переносов строк
                cleaned_balance_text = "".join(balance_element.text.split())
                print(f"[DEBIT PAGE] Текст баланса в модальном окне после очистки: '{cleaned_balance_text}'")
                
                assert "999999999999,99" in cleaned_balance_text, f"Ошибка: Сумма баланса в списке 'Все счета' отображается неверно! Текст: {cleaned_balance_text}"
                assert "₽" in cleaned_balance_text, "Ошибка: Значок валюты '₽' отсутствует в строке списка!"
            
            # 3. ПРОВЕРКА ИКОНКИ КАРТОЧКИ ПО АТРИБУТУ ALT
            with allure.step("Проверить отображение правильной кастомной иконки у счета в списке"):
                # Ищем картинку глобально по уникальному alt (имени счета)
                icon_xpath = f"//img[@alt='{name}']"
                icon_element = WebDriverWait(self.driver, 5).until(
                    EC.visibility_of_element_located((By.XPATH, icon_xpath))
                )
                assert icon_element.is_displayed(), f"Иконка оформления для счета '{name}' не отображается в списке!"
                print(f"[DEBIT PAGE] УСПЕХ! Карточка в списке содержит верную иконку лапки.")
                
        except Exception as e:
            raise AssertionError(f"Не удалось выполнить проверку счета '{name}' в окне 'Все счета'! Ошибка: {e}")

    @allure.step("Выполнить визуальную проверку страницы по скриншоту-эталону '{baseline_name}'")
    def verify_visual_screenshot(self, baseline_name: str):
        """
        Делает скриншот страницы и сравнивает его с эталоном пиксель-в-пиксель.
        Если эталона нет — создает его автоматически.
        """
        # Настраиваем папки для хранения картинок
        base_dir = "screenshots"
        baseline_path = os.path.join(base_dir, "baselines", f"{baseline_name}.png")
        actual_path = os.path.join(base_dir, "actual", f"{baseline_name}_actual.png")
        diff_path = os.path.join(base_dir, "diff", f"{baseline_name}_diff.png")
        
        # Создаем папки, если их нет
        os.makedirs(os.path.join(base_dir, "baselines"), exist_ok=True)
        os.makedirs(os.path.join(base_dir, "actual"), exist_ok=True)
        os.makedirs(os.path.join(base_dir, "diff"), exist_ok=True)
        
        # Небольшая пауза, чтобы анимация интерфейса полностью остановилась перед снимком
        time.sleep(1)
        
        # 1. Делаем фактический снимок экрана
        self.driver.save_screenshot(actual_path)
        allure.attach.file(actual_path, name="Фактический скриншот (Actual)", attachment_type=allure.attachment_type.PNG)
        
        # 2. Если эталона еще нет (первый запуск) — сохраняем текущий снимок как эталон
        if not os.path.exists(baseline_path):
            self.driver.save_screenshot(baseline_path)
            allure.attach.file(baseline_path, name="Создан новый эталон (Baseline)", attachment_type=allure.attachment_type.PNG)
            print(f"\n[VISUAL] Создан новый скриншот-эталон: {baseline_path}")
            print("[VISUAL] При следующем прогоне этот тест будет сравниваться с ним.")
            return

        # 3. Сравниваем фактический скриншот с сохраненным эталоном
        img_baseline = Image.open(baseline_path).convert('RGB')
        img_actual = Image.open(actual_path).convert('RGB')
        
        # Находим разницу между картинками
        diff = ImageChops.difference(img_baseline, img_actual)
        
        # Если разница есть (getbbox вернет координаты несовпадающих пикселей)
        if diff.getbbox():
            # Сохраняем картинку с разницей и крепим всё в Allure для дебага
            diff.save(diff_path)
            allure.attach.file(baseline_path, name="Эталонный скриншот (Baseline)", attachment_type=allure.attachment_type.PNG)
            allure.attach.file(diff_path, name="Разница в верстке (Diff)", attachment_type=allure.attachment_type.PNG)
            
            raise AssertionError(
                f"Визуальная проверка провалена! Обнаружены расхождения с фото-эталоном '{baseline_name}'. "
                f"Посмотрите разницу (Diff) в отчете Allure."
            )
        else:
            print(f"[VISUAL] Успех! Страница полностью соответствует скриншот-эталону '{baseline_name}'.")

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

# === FILE: tests/auth/test_login.py===
import os  # Импортируем стандартный модуль для работы с ОС
from pages.auth_pages.welcome_page import WelcomePage
from pages.auth_pages.login_page import LoginPage
from pages.dashboard_pages.dashboard_page import DashboardPage

def test_user_can_login_successfully(driver):
    welcome_page = WelcomePage(driver)
    login_page = LoginPage(driver)
    dashboard_page = DashboardPage(driver)
    
    welcome_page.open()
    welcome_page.click_login_button()
    
    # Достаем секретные данные из файла .env через os.getenv
    email = os.getenv("PROFINANSY_USER_EMAIL")
    password = os.getenv("PROFINANSY_USER_PASSWORD")
    
    # Передаем скрытые переменные в методы страницы
    login_page.enter_email(email)
    login_page.enter_password(password)
    
    login_page.click_submit_button()
    
    # Проверка
    is_header_visible = dashboard_page.is_my_money_header_visible()
    assert is_header_visible, "Авторизация провалилась! Заголовок 'Мои деньги' не найден."
    
    print("\n[ТЕСТ] Сценарий авторизации выполнен безопасно!")

# === FILE: tests/auth/test_registration.py===
import pytest
from pages.auth_pages.welcome_page import WelcomePage
from pages.auth_pages.registration_page import RegistrationPage

class TestWebRegistration:
    
    def test_wal_t301_registration_flow(self, driver):
        """WAL-T301: Регистрация через почту (Позитивный сценарий)"""
        welcome_page = WelcomePage(driver)
        registration_page = RegistrationPage(driver)
        
        # 1 Step: Перейти на страницу welcome
        welcome_page.open()
        
        # 2 Step: Тап на "Регистрация"
        welcome_page.click_register_button()
        
        # 3 Step: Ввести валидный email
        registration_page.enter_email("new_qa_user@mails.org")
        
        # Expected: Пока не выбраны оба чек-бокса кнопка "Остался один шаг" задизайблена
        assert not registration_page.is_one_step_button_enabled(), "Кнопка активна без чек-боксов!"
        
        # 4 Step: Выбрать оба чек-бокса
        registration_page.select_all_checkboxes()
        
        # Expected: Кнопка "Остался один шаг" активна
        assert registration_page.is_one_step_button_enabled(), "Кнопка не стала активной!"
        
        # 5 Step: Клик на кнопку
        registration_page.click_one_step_left()

    def test_wal_t302_email_with_leading_space(self, driver):
        """WAL-T302: Регистрация через почту: ввод адреса почты с пробелом спереди"""
        registration_page = RegistrationPage(driver)
        
        registration_page.open_directly()
        registration_page.enter_email(" test@mails.org")
        
        error = registration_page.get_email_error_text()
        assert "Некорректный e-mail" in error, "Ошибка валидации пробела не появилась"

    def test_wal_t304_email_without_at_symbol(self, driver):
        """WAL-T304: Регистрация через почту: ввод адреса почты без @"""
        registration_page = RegistrationPage(driver)
        
        registration_page.open_directly()
        registration_page.enter_email("anna1038yandex.ru")
        
        error = registration_page.get_email_error_text()
        assert "Некорректный e-mail" in error, "Система пропустила email без @"

# === FILE: tests/debit_accounts/creation/test_account_empty_state_visual.py===
import allure
from pages.dashboard_pages.dashboard_page import DashboardPage
from pages.debit_pages.accounts_main_page import AccountsMainPage

@allure.feature("Бюджет и Счета")
@allure.story("Визуальное тестирование (Скриншоты)")
@allure.title("Проверка вёрстки пустого состояния страницы счетов по скриншоту-эталону")
def test_account_empty_state_visual_by_screenshot(logged_in_driver):
    dashboard_page = DashboardPage(logged_in_driver)
    accounts_page = AccountsMainPage(logged_in_driver)
    
    # 1. Переходим в раздел "Счета"
    with allure.step("Перейти в раздел 'Счета' через главное меню"):
        assert dashboard_page.is_my_money_header_visible(), "Главная страница дашборда не загрузилась!"
        dashboard_page.open_accounts_section()
        assert accounts_page.is_page_loaded(), "Раздел 'Счета' не открылся!"
    
    # 2. Запускаем строгую попиксельную проверку экрана по фото-эталону
    accounts_page.verify_visual_screenshot("account_empty_state_baseline")

# === FILE: tests/debit_accounts/creation/test_account_name_too_long.py===
import allure
import time
from pages.dashboard_pages.dashboard_page import DashboardPage
from pages.debit_pages.accounts_main_page import AccountsMainPage

@allure.feature("Бюджет и Счета")
@allure.story("Управление дебетовыми счетами")
@allure.title("Проверка валидации: слишком длинное название счёта (>100 символов)")
def test_error_when_account_name_is_too_long(logged_in_driver):
    dashboard_page = DashboardPage(logged_in_driver)
    accounts_page = AccountsMainPage(logged_in_driver)
    
    with allure.step("Перейти в раздел 'Счета' через главное меню"):
        assert dashboard_page.is_my_money_header_visible(), "Не удалось загрузить дашборд!"
        dashboard_page.open_accounts_section()
        assert accounts_page.is_page_loaded(), "Раздел 'Счета' не загрузился!"
    
    with allure.step("Открыть форму создания и ввести слишком длинное название"):
        accounts_page.click_create_account_button()
        accounts_page.select_debit_account_type()
        accounts_page.click_continue_if_exists()
        
        long_name = "1" * 101
        accounts_page.enter_account_name(long_name)
        accounts_page.click_save_button()
    
    with allure.step("Проверить появление ошибки валидации"):
        assert accounts_page.is_too_long_error_visible(), "Ошибка 'Слишком длинное название' не отобразилась!"

# === FILE: tests/debit_accounts/creation/test_account_required_fields.py===
import time
from pages.dashboard_pages.dashboard_page import DashboardPage
from pages.debit_pages.accounts_main_page import AccountsMainPage

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
    # Метод .text в Selenium собирает текст из элемента и всех его дочерних тегов (например, span со звездочкой)
    name_label = accounts_page.get_account_name_label_text()
    currency_label = accounts_page.get_currency_label_text()
    
    assert "*" in name_label, f"У поля 'Название счета' нет красной звездочки! Текст: '{name_label}'"
    assert "*" in currency_label, f"У поля 'Валюта счета' нет красной звездочки! Текст: '{currency_label}'"
    print("[ТЕСТ] Проверка наличия звёздочек у обязательных полей — УСПЕШНО")
    
    # 4. Кликаем на кнопку "Сохранить", оставив поля пустыми
    accounts_page.click_save_button()
    
    # 5. ПРОВЕРКА ТЕКСТА ОШИБОК ВАЛИДАЦИИ (ASSERTS)
    assert accounts_page.is_name_required_error_visible(), "Ошибка 'Обязательное поле' не появилась под названием счета!"
    assert accounts_page.is_currency_required_error_visible(), "Ошибка 'Обязательное поле' не появилась под валютой счета!"
    
    time.sleep(2)
    print("\n[ТЕСТ] Валидация незаполненных обязательных полей успешно пройдена!")

# === FILE: tests/debit_accounts/creation/test_create_account_max_balance.py===
import time
import allure
from selenium.webdriver.common.by import By
from pages.dashboard_pages.dashboard_page import DashboardPage
from pages.debit_pages.accounts_main_page import AccountsMainPage

@allure.feature("Бюджет и Счета")
@allure.story("Управление дебетовыми счетами")
@allure.title("Успешное создание счёта с максимальным балансом и стандартной иконкой")
def test_success_create_account_with_max_balance_and_regular_icon(logged_in_driver, account_cleanup_registry):
    dashboard_page = DashboardPage(logged_in_driver)
    accounts_page = AccountsMainPage(logged_in_driver)
    
    # 1. Переходим в раздел "Счета"
    with allure.step("Перейти в раздел 'Счета' через главное меню"):
        assert dashboard_page.is_my_money_header_visible()
        dashboard_page.open_accounts_section()
        assert accounts_page.is_page_loaded()
    
    # 2. Открываем форму создания нового дебетового счета
    accounts_page.click_create_account_button()
    accounts_page.select_debit_account_type()
    accounts_page.click_continue_if_exists()
    
    # 3. Вводим уникальное название счета
    test_account_name = f"Макс Баланс-{int(time.monotonic())}"
    accounts_page.enter_account_name(test_account_name)
    
    # РЕГИСТРИРУЕМ В РЕЕСТР АВТО-УДАЛЕНИЯ (Teardown сотрет счет в конце теста)
    account_cleanup_registry.append(test_account_name)
    
    # 4. Вводим кастомный максимальный баланс 999 999 999 999.99 рублей
    accounts_page.enter_balance("999 999 999 999.99")
    
    # 5. Выбираем первую дефолтную валюту (Рубль)
    accounts_page.select_first_currency()
    
    # 6. Настраиваем оформление: выбираем первую стандартную иконку (лапку)
    accounts_page.open_icon_selection()
    accounts_page.select_first_regular_icon()
    
    # 7. Настраиваем цвет: кликаем на блок "Цвет иконки" и выбираем первый (серый)
    accounts_page.open_color_selection()
    accounts_page.select_first_color()
    
    # 8. Сохраняем счет
    accounts_page.click_save_button()
    
    # 9. Ожидаем, пока счет появится на карусели главного экрана
    accounts_page.wait_until_account_created(test_account_name)
    
    # 10. Проверяем баланс и иконку на главной карточке карусели
    accounts_page.check_card_with_huge_balance_and_icon(test_account_name)
    
    # ================= НОВЫЕ ШАГИ СЦЕНАРИЯ =================
    
    # 11. Кликаем на кнопку-иконку "Все счета" (кошелек рядом с настройками)
    accounts_page.click_all_accounts_button()
    
    # 12. Глубокая проверка счета внутри модального списка "Все счета"
    accounts_page.check_account_in_all_accounts_modal(test_account_name)
    
    time.sleep(1)
    print(f"\n[ТЕСТ] Полный триумф! Счет '{test_account_name}' проверен на карусели и в общем списке 'Все счета'.")

# === FILE: tests/debit_accounts/creation/test_create_account_no_balance.py===
import time
import allure
from selenium.webdriver.common.by import By
from pages.dashboard_pages.dashboard_page import DashboardPage
from pages.debit_pages.accounts_main_page import AccountsMainPage

@allure.feature("Бюджет и Счета")
@allure.story("Управление дебетовыми счетами")
@allure.title("Успешное создание счёта без ввода начального баланса")
# Добавили нашу новую фикстуру в аргументы функции:
def test_success_create_account_without_initial_balance(logged_in_driver, account_cleanup_registry):
    dashboard_page = DashboardPage(logged_in_driver)
    accounts_page = AccountsMainPage(logged_in_driver)
    
    with allure.step("Перейти в раздел 'Счета' через главное меню"):
        assert dashboard_page.is_my_money_header_visible()
        dashboard_page.open_accounts_section()
        assert accounts_page.is_page_loaded()
    
    accounts_page.click_create_account_button()
    accounts_page.select_debit_account_type()
    accounts_page.click_continue_if_exists()
    
    # Генерируем уникальное имя, чтобы тесты не пересекались по данным
    test_account_name = f"Автотест-{int(time.monotonic())}"
    accounts_page.enter_account_name(test_account_name)
    
    # РЕГИСТРИРУЕМ СЧЕТ НА УДАЛЕНИЕ:
    # Как только тест завершится (неважно, упадет он на ассерте или пройдет), 
    # Pytest заглянет в этот список и сотрет этот счет.
    account_cleanup_registry.append(test_account_name)
    
    accounts_page.select_first_currency()
    accounts_page.click_save_button()
    
    accounts_page.wait_until_account_created(test_account_name)
    
    with allure.step("Проверить, что на странице отображаются карточки счетов"):
        all_acc_card = logged_in_driver.find_element(By.XPATH, "//*[text()='Все счета']")
        new_acc_card = logged_in_driver.find_element(By.XPATH, f"//*[text()='{test_account_name}']")
        assert all_acc_card.is_displayed()
        assert new_acc_card.is_displayed()

    accounts_page.check_card_details(test_account_name)
    print("\n[ТЕСТ] Основные проверки создания счета завершены успешно!")

# === FILE: tests/debit_accounts/creation/test_create_account_only_with_icon.py===
import time
import allure
from selenium.webdriver.common.by import By
from pages.dashboard_pages.dashboard_page import DashboardPage
from pages.debit_pages.accounts_main_page import AccountsMainPage

@allure.feature("Бюджет и Счета")
@allure.story("Управление дебетовыми счетами")
@allure.title("Успешное создание счёта с кастомной банковской иконкой в USD и начальным балансом")
def test_success_create_account_with_bank_icon(logged_in_driver, account_cleanup_registry):
    dashboard_page = DashboardPage(logged_in_driver)
    accounts_page = AccountsMainPage(logged_in_driver)
    
    # 1. Переходим в раздел "Счета"
    with allure.step("Перейти в раздел 'Счета' через главное меню"):
        assert dashboard_page.is_my_money_header_visible()
        dashboard_page.open_accounts_section()
        assert accounts_page.is_page_loaded()
    
    # 2. Открываем форму создания счета
    accounts_page.click_create_account_button()
    accounts_page.select_debit_account_type()
    accounts_page.click_continue_if_exists()
    
    # 3. Вводим название счета
    test_account_name = f"USD Банк-{int(time.monotonic())}"
    accounts_page.enter_account_name(test_account_name)
    
    # Регистрируем в реестр авто-удаления (Teardown сработает в любом случае!)
    account_cleanup_registry.append(test_account_name)
    
    # 4. Вводим кастомный начальный баланс 150,78
    accounts_page.enter_balance("150,78")
    
    # 5. Выбираем валюту "Доллар США"
    accounts_page.select_currency_by_name("Доллар США")
    
    # 6. Настраиваем оформление (выбираем банковскую иконку)
    accounts_page.open_icon_selection()
    accounts_page.click_banks_tab()
    accounts_page.select_first_bank_icon()
    
    # 7. Сохраняем счет
    accounts_page.click_save_button()
    
    # 8. Ожидаем базовое появление счета в сетке
    accounts_page.wait_until_account_created(test_account_name)
    
    # 9. СТРОГИЕ ПРОВЕРКИ ИКОНКИ, ВАЛЮТЫ И СУММЫ (ASSERTS)
    accounts_page.check_card_with_icon_and_usd(test_account_name)
    
    time.sleep(1)
    print(f"\n[ТЕСТ] Проверка завершена! Счет '{test_account_name}' содержит иконку, баланс 150,78 и значок $. ")

# === FILE: tests/debit_accounts/creation/test_delete_account.py===
import time
import pytest
import allure
from pages.dashboard_pages.dashboard_page import DashboardPage
from pages.debit_pages.accounts_main_page import AccountsMainPage

# === ФИКСТУРА ПРЕДУСТАНОВКИ (SETUP) ===
@pytest.fixture(scope="function")
def setup_debit_account(logged_in_driver):
    """Фикстура автоматического создания дебетового счета перед началом теста на удаление"""
    dashboard_page = DashboardPage(logged_in_driver)
    accounts_page = AccountsMainPage(logged_in_driver)
    
    # Генерируем уникальное имя, чтобы тесты на разных доменах не конфликтовали
    unique_account_name = f"Удаление-{int(time.monotonic())}"
    
    print(f"\n[FIXTURE SETUP] Создаем тестовый счет для последующего удаления: '{unique_account_name}'")
    
    assert dashboard_page.is_my_money_header_visible()
    dashboard_page.open_accounts_section()
    assert accounts_page.is_page_loaded()
    
    # Проходим шаги создания
    accounts_page.click_create_account_button()
    accounts_page.select_debit_account_type()
    accounts_page.click_continue_if_exists()
    accounts_page.enter_account_name(unique_account_name)
    accounts_page.select_first_currency()
    accounts_page.click_save_button()
    
    # Ждем успешного создания сущности
    accounts_page.wait_until_account_created(unique_account_name)
    print("[FIXTURE SETUP] Тестовый счет успешно подготовлен.")
    
    # Передаем имя созданного счета прямо в тестовую функцию
    yield unique_account_name


# === САМ ТЕСТ-КЕЙС ===
@allure.feature("Бюджет и Счета")
@allure.story("Управление дебетовыми счетами")
@allure.title("Успешное удаление дебетового счёта через двухэтапное подтверждение")
def test_success_delete_debit_account(logged_in_driver, setup_debit_account):
    # Принимаем имя счёта из фикстуры выше
    target_account_name = setup_debit_account
    accounts_page = AccountsMainPage(logged_in_driver)
    
    # 1. Нажимаем 3 точки на созданной карточке
    accounts_page.click_three_dots_for_account(target_account_name)
    
    # 2. Выбираем Удалить счет в выпадающем списке
    accounts_page.click_delete_account_in_dropdown()
    
    # 3. Кликаем 'Удалить счет' в первом модальном окне предупреждения
    accounts_page.click_confirm_delete_first_stage()
    
    # 4. Проставляем оба чекбокса согласия во втором модальном окне
    accounts_page.tick_both_delete_checkboxes()
    
    # 5. Нажимаем финальную активировавшуюся кнопку 'Удалить счет'
    accounts_page.click_confirm_delete_final_stage()
    
    # 6. ГЛАВНАЯ ПРОВЕРКА (ASSERT): убеждаемся, что карточка пропала из интерфейса
    accounts_page.assert_account_is_deleted(target_account_name)
    
    print(f"\n[ТЕСТ] УСПЕХ! Счет '{target_account_name}' успешно удален со всеми шагами проверок.")

# === FILE: tests/debit_accounts/creation/test_empty_accounts.py===
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

# === FILE: tests/debit_accounts/modification/conftest.py===
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

# === FILE: tests/debit_accounts/modification/test_change_name.py===
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





