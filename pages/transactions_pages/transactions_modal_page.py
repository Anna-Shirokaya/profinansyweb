import time
import datetime
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, ElementNotInteractableException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains

class TransactionsModalPage:
    def __init__(self, driver):
        self.driver = driver

        # --- ЛОКАТОРЫ ВКЛАДОК И ПОЛЕЙ ---
        #поле откуда перевод
        self.SOURCE_ACCOUNT_TRIGGER = (
            By.XPATH, 
            "//input[@name='expenseWallet'] | "
            "//div[contains(@class, 'InputField-root') and .//label[contains(., 'Откуда')]]//input"
        )

        #поле куда перевод
        self.DESTINATION_ACCOUNT_TRIGGER = (
            By.XPATH, 
            "//input[@name='accumulationWallet'] | "
            "//div[contains(@class, 'InputField-root') and .//label[contains(., 'Куда')]]//input"
        )

        #вкладка Накопления
        self.ACCUMULATION_TAB = (
            By.XPATH, 
            "//div[contains(@class, 'transaction-swiper-type') and .//p[text()='Накопления']]"
        )

        #вкладка Расход
        self.EXPENSE_TAB = (
            By.XPATH, 
            "//div[contains(@class, 'transaction-swiper-type') and .//p[text()='Расход']]"
        )
        #вкладка Доход
        self.INCOME_TAB = (
            By.XPATH, 
            "//div[contains(@class, 'transaction-swiper-type') and .//p[text()='Доход']]"
        )

        #вкладка Переводы
        self.TRANSFER_TAB = (
            By.XPATH, 
            "//div[contains(@class, 'transaction-swiper-type') and .//p[text()='Переводы']]"
        )

        #вкладка Займы
        self.DEBT_TAB = (
            By.XPATH, 
            "//div[contains(@class, 'transaction-swiper-type') and .//p[text()='Займы']]"
        )

        #Название формы создания транзакций - Транзакция
        self.MODAL_TITLE = (By.XPATH, "//span[contains(@class, 'sideModal-title') and text()='Транзакция']")

        #поле для ввода суммы
        self.AMOUNT_INPUT = (
            By.XPATH, 
            "//input[@placeholder='0'] | "
            "//*[contains(text(), 'Сумма')]/following::input[1]"
        )

        #описание поля для ввода суммы
        self.AMOUNT_LABEL = (By.XPATH, "//label[contains(., 'Сумма')]")

        self.CALCULATOR_ICON = (By.XPATH, "//span[contains(@class, 'input-icon')]//*[local-name()='svg']")

        self.WHAT_SPENT_LABEL = (By.XPATH, "//*[text()='На что потратили']")

        self.WHAT_SPENT_INPUT = (By.XPATH, "//input[@placeholder='Например: Кофе']")

        #иконка лупы у поля на что потратили
        self.MAGNIFIER_ICON = (
            By.XPATH, 
            "//input[@name='expenseName']/following-sibling::span[contains(@class, 'input-icon')]"
        )

        self.SOURCE_ACCOUNT_LABEL = (By.XPATH, "//*[text()='Откуда была произведена трата']")

        self.EXPENSE_TYPE_LABEL = (By.XPATH, "//*[text()='Тип расхода']")

        self.EXPENSE_TYPE_INPUT = (By.XPATH, "//input[@placeholder='Начните ввод']")

        self.WHEN_SPENT_LABEL = (By.XPATH, "//*[text()='Когда потратили']")

        self.WHEN_SPENT_INPUT = (By.XPATH, "//*[text()='Когда потратили']/following::input[1]")

        self.ADD_TAG_BUTTON = (By.XPATH, "//*[contains(text(), 'Добавить тег')]")

        self.NOTES_LABEL = (By.XPATH, "//*[text()='Место для вашей заметки']")

        self.NOTES_INPUT = (By.XPATH, "//textarea[@placeholder='Поле ввода'] | //input[@placeholder='Поле ввода']")

        

        self.SUBMIT_BUTTON = (
            By.XPATH, 
            "//button[./span[text()='Создать']] | "
            "//button[contains(., 'Создать')] | "
            "//div[contains(@class, 'sidebarSlides')]//button"
        )

        self.REQUIRED_FIELD_ERRORS = (By.XPATH, "//*[text()='Обязательное поле']")

        #локаторы для вкладки расход
        self.CALCULATOR_ICON = (
            By.XPATH, 
            "//input[@placeholder='0']/following-sibling::*//*[local-name()='svg'] | //*[contains(@class, 'calc') or contains(@class, 'Calculator')]"
        )

        self.WHAT_SPENT_LABEL = (By.XPATH, "//*[text()='На что потратили']")
        self.WHAT_SPENT_INPUT = (By.XPATH, "//input[@placeholder='Например: Кофе']")
        self.MAGNIFIER_ICON = (
            By.XPATH, 
            "//input[@placeholder='Например: Кофе']/following-sibling::*//*[local-name()='svg']"
        )

        self.SOURCE_ACCOUNT_LABEL = (By.XPATH, "//*[text()='Откуда была произведена трата']")

        self.EXPENSE_TYPE_LABEL = (By.XPATH, "//*[text()='Тип расхода']")
        self.EXPENSE_TYPE_INPUT = (By.XPATH, "//input[@placeholder='Начните ввод']")

        self.WHEN_SPENT_LABEL = (By.XPATH, "//*[text()='Когда потратили']")
        self.WHEN_SPENT_INPUT = (By.XPATH, "//*[text()='Когда потратили']/following::input[1]")

        self.ADD_TAG_BUTTON = (By.XPATH, "//*[contains(text(), 'Добавить тег')]")
        self.NOTES_LABEL = (By.XPATH, "//*[text()='Место для вашей заметки']")
        self.NOTES_INPUT = (By.XPATH, "//textarea[@placeholder='Поле ввода'] | //input[@placeholder='Поле ввода']")

        self.FIELD_LABEL_BY_NAME = lambda field_name: (
            By.XPATH, 
            f"//*[contains(text(), '{field_name}')]"
        )

        self.MANDATORY_FIELD_ASTERISK_BY_NAME = lambda field_name: (
            By.XPATH, 
            f"//*[contains(text(), '{field_name}') and contains(., '*')] | "
            f"//*[contains(text(), '{field_name}')]//following-sibling::*[contains(text(), '*')] | "
            f"//*[contains(text(), '{field_name}')]/span[contains(text(), '*')]"
        )

        # --- Локаторы создания типа расхода (WAL-T519) ---
        self.EXPENSE_TYPE_DROPDOWN = (By.XPATH, "//input[@placeholder='Начните ввод']/ancestor::div[contains(@class, 'Select') or contains(@class, 'field')][1] | //*[contains(text(), 'Тип расхода')]/following::input[1]")
        self.ADD_NEW_TYPE_BTN = (
            By.XPATH, 
            "//button[contains(@class, 'createTransactionBtn')]"
        )
        self.CREATE_TYPE_MODAL_TITLE = (By.XPATH, "//*[text()='Создание типа расхода']")

# Поля формы создания типа расхода
        self.TYPE_CATEGORY_SELECT = (
            By.XPATH, 
            "//input[@value='Категория'] | //*[text()='Категория']/following::div[contains(@class, 'inputWrapper')][1]"
        )
        self.CATEGORY_VARIABLE_OPTION = (
            By.XPATH, 
            "//li[text()='Переменные'] | //*[contains(@class, 'Select')]//*[text()='Переменные'] | //*[text()='Переменные']"
        )
        self.TYPE_NAME_INPUT = (By.XPATH, "//input[@placeholder='Название типа транзакции' or @name='typeName']")

# Иконка и цвет типа
        self.TYPE_ICON_TRIGGER = (
            By.XPATH, 
            "//*[contains(text(), 'Иконка типа расхода')]/ancestor::button[1] | //*[contains(text(), 'Иконка типа расхода')]"
        )
        self.FIRST_TYPE_ICON_IMG = (
            By.XPATH, 
            "(//div[contains(@class, 'style_iconWrapper')]//img[contains(@class, 'style_iconImg')])[1]"
        )
        self.TYPE_COLOR_TRIGGER = (
            By.XPATH, 
            "//*[contains(text(), 'Цвет иконки')]/ancestor::button[1] | //*[contains(text(), 'Цвет иконки')]"
        )
        self.FIRST_TYPE_COLOR = (
            By.XPATH, 
            "(//button[contains(@class, 'style_colorItemWrapper')])[1]"
        )
        
        self.SAVE_TYPE_BTN = (
            By.XPATH, 
            "//div[contains(@class, 'confirmBtns')]//button[contains(@class, 'confirmBtn') and .//span[text()='Создать']]"
        )

        # 2. Кнопка "Создать" в главной форме транзакции (боковая шторка)
        self.SUBMIT_TRANSACTION_BTN = (
            By.XPATH, 
            "//div[contains(@class, 'sidebarSlides')]//button[.//span[text()='Создать']]"
        )

    # --- МЕТОДЫ ВЗАИМОДЕЙСТВИЯ ---

    def _close_dropdowns_safely(self):
        """Безопасный клик по лейблу, чтобы React закрыл все выпадающие списки"""
        try:
            lbl = self.driver.find_element(By.XPATH, "//label[contains(text(), 'Сумма') or contains(text(), 'Когда')]")
            ActionChains(self.driver).click(lbl).perform()
            time.sleep(0.3)
        except Exception:
            pass

    def _safe_type(self, locator, text):
        """Надежный ввод: выделяет всё, очищает и печатает текст без склеивания"""
        inp = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(locator))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", inp)
        
        try:
            inp.click()
        except (ElementNotInteractableException, ElementClickInterceptedException):
            self.driver.execute_script("arguments[0].click();", inp)
            
        time.sleep(0.2)
        
        # Надежная очистка поля
        inp.send_keys(Keys.CONTROL + "a")
        inp.send_keys(Keys.BACKSPACE)
        
        # Добиваем JavaScript'ом, если обычный Backspace не сработал
        self.driver.execute_script("arguments[0].value = ''; arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", inp)
        time.sleep(0.2)
        
        inp.send_keys(text)
        return inp

    @allure.step("Проверить видимость вкладки 'Накопления'")
    def is_accumulation_tab_visible(self) -> bool:
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(self.ACCUMULATION_TAB)
            )
            return element.is_displayed()
        except TimeoutException:
            return False

    @allure.step("Перейти на вкладку 'Накопления' в модальном окне")
    def open_accumulation_tab(self):
        tab = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable(self.ACCUMULATION_TAB)
        )
        try:
            tab.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", tab)
            
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Откуда произведен перевод')]"))
        )
        print("[TRANSACTION MODAL] Переход на вкладку 'Накопления' успешно выполнен.")
        time.sleep(0.5)

    @allure.step("Выбрать счет '{account_name}' в поле 'Откуда'")
    def select_source_account(self, account_name: str):
        self._close_dropdowns_safely()
        self._safe_type(self.SOURCE_ACCOUNT_TRIGGER, account_name)
        time.sleep(1.5) # Ждем, пока отфильтруется список
        
        # Ищем пункт списка по тексту и названию класса (включая упомянутый вами ListItem)
        option_xpath = f"//*[contains(@class, 'ListItem') or contains(@class, 'option') or @role='option']//*[contains(text(), '{account_name}')] | //div[contains(text(), '{account_name}') and not(self::input) and not(ancestor::*[contains(@class, 'InputField')])]"
        
        options = self.driver.find_elements(By.XPATH, option_xpath)
        clicked = False
        
        for opt in options:
            if opt.is_displayed():
                try:
                    # Кликаем классическим Selenium
                    opt.click()
                except Exception:
                    # Если перекрыто - кликаем через JS
                    self.driver.execute_script("arguments[0].click();", opt)
                clicked = True
                break
                
        if not clicked:
            raise Exception(f"[MODAL] ОШИБКА: Не удалось найти в списке и кликнуть по счету '{account_name}'")
            
        time.sleep(0.5)
        self._close_dropdowns_safely()
        print(f"[MODAL] Счет '{account_name}' успешно выбран в поле 'Откуда'.")

    @allure.step("Проверить наличие счета '{account_name}' в списке 'Куда'")
    def is_account_in_destination_dropdown(self, account_name: str) -> bool:
        self._close_dropdowns_safely()
        self._safe_type(self.DESTINATION_ACCOUNT_TRIGGER, account_name)
        time.sleep(1.5)

        # 1. Проверяем плашку "Не найдено"
        not_found = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Не найдено')]")
        is_not_found = any(elem.is_displayed() for elem in not_found)

        # 2. Ищем элемент списка
        option_xpath = f"//*[contains(@class, 'ListItem') or contains(@class, 'option') or @role='option']//*[contains(text(), '{account_name}')] | //div[contains(text(), '{account_name}') and not(self::input) and not(ancestor::*[contains(@class, 'InputField')])]"
        options = self.driver.find_elements(By.XPATH, option_xpath)
        is_visible = any(opt.is_displayed() for opt in options)

        self._close_dropdowns_safely()

        if is_not_found:
            print(f"[MODAL] [Куда] Счет '{account_name}' НЕ НАЙДЕН.")
            return False

        print(f"[MODAL] [Куда] Результат поиска счета '{account_name}': {is_visible}")
        return is_visible

    @allure.step("Открыть выпадающий список 'Счет пополнения'")
    def open_destination_account_dropdown(self):
        trigger = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.DESTINATION_ACCOUNT_TRIGGER)
        )
        try:
            trigger.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", trigger)
        time.sleep(0.3)

    @allure.step("Выбрать счет пополнения '{account_name}'")
    def select_destination_account(self, account_name: str):
        """Вводит название счета в поле 'Куда' и нажимает на найденный элемент"""
        self._close_dropdowns_safely()
        self._safe_type(self.DESTINATION_ACCOUNT_TRIGGER, account_name)
        time.sleep(1.5)

        option_xpath = (
            f"//*[contains(@class, 'ListItem') or contains(@class, 'option') or @role='option']//*[contains(text(), '{account_name}')] | "
            f"//div[contains(text(), '{account_name}') and not(self::input) and not(ancestor::*[contains(@class, 'InputField')])]"
        )
        
        options = self.driver.find_elements(By.XPATH, option_xpath)
        clicked = False
        
        for opt in options:
            if opt.is_displayed():
                try:
                    opt.click()
                except Exception:
                    self.driver.execute_script("arguments[0].click();", opt)
                clicked = True
                break
                
        if not clicked:
            raise Exception(f"[MODAL] ОШИБКА: Не удалось найти в списке и кликнуть по счету '{account_name}' в поле 'Куда'")
            
        time.sleep(0.5)
        self._close_dropdowns_safely()
        print(f"[MODAL] Счет '{account_name}' успешно выбран в поле 'Куда'.")

    @allure.step("Ввести сумму операции '{amount}'")
    def enter_amount(self, amount: str):
        self._safe_type(self.AMOUNT_INPUT, amount)

    @allure.step("Нажать 'Создать' (сохранить транзакцию)")
    def click_submit_button(self):
        """Нажимает 'Создать' и дожидается полного закрытия модального окна транзакции."""
        submit_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.SUBMIT_TRANSACTION_BTN)
        )
        
        try:
            submit_btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", submit_btn)

        # 1. Ждем исчезновения боковой шторки/оверлея из DOM
        WebDriverWait(self.driver, 10).until_not(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".sideModal-overlay, [role='dialog']"))
        )
        
        # 2. Небольшая пауза для завершения перерисовки истории операций в React
        time.sleep(1.5)
        print("[TRANSACTIONS MODAL] Модальное окно транзакции полностью закрыто.")

    @allure.step("Создать транзакцию накопления: с '{source}' на '{destination}' сумму '{amount}'")
    def create_accumulation_transaction(self, source: str, destination: str, amount: str):
        from pages.dashboard_pages.dashboard_page import DashboardPage
        dashboard = DashboardPage(self.driver)
        
        dashboard.open_add_transaction_modal()
        self.open_accumulation_tab()
        self.select_source_account(source)
        self.select_destination_account(destination)
        self.enter_amount(amount)
        self.click_submit_button()

    @allure.step("Проверить отображение всех полей формы 'Накопления'")
    def check_accumulation_form_fields_present(self):
        fields = ["Сумма", "Когда начислено", "Откуда произведен перевод", "Куда переводим", "Место для вашей заметки"]
        for field in fields:
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(self.FIELD_LABEL_BY_NAME(field))
            )
        return True

    @allure.step("Проверить, что обязательные поля отмечены звездочкой (*)")
    def check_mandatory_fields_asterisks(self):
        mandatory_fields = ["Сумма", "Когда начислено", "Откуда произведен перевод", "Куда переводим"]
        for field in mandatory_fields:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(self.MANDATORY_FIELD_ASTERISK_BY_NAME(field))
            )
        return True

    @allure.step("Проверить, что кнопка 'Создать' неактивна (задизейблена)")
    def is_submit_button_disabled(self):
        btn = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(self.SUBMIT_BUTTON))
        
        is_html_disabled = btn.get_attribute("disabled") is not None
        is_aria_disabled = btn.get_attribute("aria-disabled") == "true"
        is_class_disabled = "disabled" in btn.get_attribute("class").lower()
        is_selenium_disabled = not btn.is_enabled()
        
        return is_html_disabled or is_aria_disabled or is_selenium_disabled or is_class_disabled

    @allure.step("Открыть выпадающий список 'Откуда произведен перевод'")
    def open_source_account_dropdown(self):
        inp = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.SOURCE_ACCOUNT_TRIGGER)
        )
        inp.click()
        time.sleep(0.5)

    @allure.step("Проверить наличие счета '{account_name}' в списке 'Откуда'")
    def is_account_in_source_dropdown(self, account_name: str) -> bool:
        self._close_dropdowns_safely()
        self._safe_type(self.SOURCE_ACCOUNT_TRIGGER, account_name)
        time.sleep(1)

        not_found = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Не найдено')]")
        if any(elem.is_displayed() for elem in not_found):
            self._close_dropdowns_safely()
            return False

        option_xpath = f"//*[contains(@class, 'ListItem') or contains(@class, 'option')]//*[contains(text(), '{account_name}')] | //div[contains(text(), '{account_name}') and not(self::input)]"
        options = self.driver.find_elements(By.XPATH, option_xpath)
        is_visible = any(opt.is_displayed() for opt in options)

        self._close_dropdowns_safely()
        return is_visible

    #методы для проверки вкладки Расход
    @allure.step("Проверить корректность элементов формы 'Транзакция (Расход)' [WAL-T518]")
    def verify_expense_form_elements(self, expected_account_name: str):
        # 1. Заголовок
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(self.MODAL_TITLE))
        
        # 2. Активная вкладка «Расход»
        with allure.step("Проверить активность вкладки 'Расход'"):
            expense_tab = self.driver.find_element(*self.EXPENSE_TAB)
            assert expense_tab.is_displayed(), "Вкладка 'Расход' не отображается!"

        # 3. Поле «Сумма» (обязательное, 0, калькулятор)
        with allure.step("Проверить поле 'Сумма *'"):
            amount_label = self.driver.find_element(*self.AMOUNT_LABEL).text
            assert "*" in amount_label, "У поля 'Сумма' нет красной звездочки!"
            amount_input = self.driver.find_element(*self.AMOUNT_INPUT)
            assert amount_input.get_attribute("placeholder") == "0", "Плейсхолдер суммы не равен '0'!"
            assert self.driver.find_element(*self.CALCULATOR_ICON).is_displayed(), "Иконка калькулятора не найдена!"

        # 4. Поле «На что потратили» (необязательное, Например: Кофе, лупа)
        with allure.step("Проверить поле 'На что потратили'"):
            what_spent_label = self.driver.find_element(*self.WHAT_SPENT_LABEL).text
            assert "*" not in what_spent_label, "У необязательного поля 'На что потратили' присутствует звездочка!"
            what_spent_input = self.driver.find_element(*self.WHAT_SPENT_INPUT)
            assert what_spent_input.get_attribute("placeholder") == "Например: Кофе", "Неверный плейсхолдер 'На что потратили'!"
            assert self.driver.find_element(*self.MAGNIFIER_ICON).is_displayed(), "Иконка лупы не найдена!"

        # 5. Поле «Откуда была произведена трата» (обязательное)
        with allure.step("Проверить поле 'Откуда была произведена трата *'"):
            source_label = self.driver.find_element(*self.SOURCE_ACCOUNT_LABEL).text
            assert "*" in source_label, "У поля 'Откуда была произведена трата' нет звездочки!"

        # 6. Поле «Тип расхода» (обязательное, Начните ввод)
        with allure.step("Проверить поле 'Тип расхода *'"):
            type_label = self.driver.find_element(*self.EXPENSE_TYPE_LABEL).text
            assert "*" in type_label, "У поля 'Тип расхода' нет звездочки!"
            type_input = self.driver.find_element(*self.EXPENSE_TYPE_INPUT)
            assert type_input.get_attribute("placeholder") == "Начните ввод", "Неверный плейсхолдер 'Тип расхода'!"

        # 7. Поле «Когда потратили» (обязательное, текущая дата)
        with allure.step("Проверить поле 'Когда потратили *'"):
            when_label = self.driver.find_element(*self.WHEN_SPENT_LABEL).text
            assert "*" in when_label, "У поля 'Когда потратили' нет звездочки!"
            today_str = datetime.datetime.now().strftime("%d.%m.%Y")
            when_input = self.driver.find_element(*self.WHEN_SPENT_INPUT)
            current_val = when_input.get_attribute("value") or when_input.get_attribute("placeholder")
            assert today_str in current_val, f"Дата '{current_val}' не совпадает с сегодня '{today_str}'!"

        # 8. Кнопка «Добавить тег» и заметок
        with allure.step("Проверить кнопку 'Добавить тег' и заметки"):
            assert self.driver.find_element(*self.ADD_TAG_BUTTON).is_displayed(), "Кнопка 'Добавить тег' не отображается!"
            notes_label = self.driver.find_element(*self.NOTES_LABEL).text
            assert "*" not in notes_label, "У поля заметок не должно быть звездочки!"
            notes_input = self.driver.find_element(*self.NOTES_INPUT)
            assert notes_input.get_attribute("placeholder") == "Поле ввода", "Неверный плейсхолдер заметок!"

    @allure.step("Проверить ошибки 'Обязательное поле' для Суммы и Типа расхода [WAL-T518]")
    def verify_validation_errors(self):
        errors = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located(self.REQUIRED_FIELD_ERRORS)
        )
        assert len(errors) >= 2, f"Ожидалось минимум 2 ошибки 'Обязательное поле', найдено: {len(errors)}"
        for err in errors:
            assert err.is_displayed(), "Сообщение об ошибке валидации не отображается!"

    @allure.step("Открыть форму создания нового типа расхода [WAL-T519]")

    def open_create_expense_type_modal(self):
        """Клик по полю 'Тип расхода' и последующий клик по появившейся кнопке '+' справа."""
        # 1. Кликаем по полю ввода типа расхода
        expense_type_input = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.EXPENSE_TYPE_DROPDOWN)
        )
        expense_type_input.click()
        time.sleep(0.5)

        # 2. Кликаем по кнопке '+' (style_createTransactionBtn) справа
        add_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.ADD_NEW_TYPE_BTN)
        )
        try:
            add_btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", add_btn)

        # 3. Дожидаемся загрузки формы 'Создание типа расхода'
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.CREATE_TYPE_MODAL_TITLE)
        )
        print("[TRANSACTIONS MODAL] Форма 'Создание типа расхода' успешно открыта.")

    @allure.step("Заполнить и сохранить новый тип расхода '{type_name}'")
    def create_new_expense_type(self, type_name: str, category: str = "Переменные"):
        # 1. Выбор категории
        category_trigger = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.TYPE_CATEGORY_SELECT))
        category_trigger.click()
    
        option = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.CATEGORY_VARIABLE_OPTION))
        option.click()

        # 2. Ввод названия
        name_input = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(self.TYPE_NAME_INPUT))
        name_input.click()
        name_input.clear()
        name_input.send_keys(type_name)

        trigger = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.TYPE_ICON_TRIGGER)
        )
        try:
            trigger.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", trigger)

        # 2. Явное ожидание 20 секунд появление первой картинки в DOM (учитывает 10 сек рендера)
        icon_img = WebDriverWait(self.driver, 20).until(
            EC.visibility_of_element_located(self.FIRST_TYPE_ICON_IMG)
        )

        # Стабилизирующая пауза 1.5 сек на фиксацию элементов в списках React
        time.sleep(1.5)

        # 3. Клик по обертке div.style_iconWrapper
        icon_wrapper = icon_img.find_element(By.XPATH, "./ancestor::div[contains(@class, 'style_iconWrapper')][1]")
        try:
            icon_wrapper.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", icon_wrapper)

        print("[TRANSACTIONS MODAL] Первая иконка типа расхода успешно выбрана.")

        # 4. Выбор цвета
        trigger = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.TYPE_COLOR_TRIGGER)
        )
        try:
            trigger.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", trigger)

        # 2. Ждем появления кнопки цвета (style_colorItemWrapper)
        color_btn = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.FIRST_TYPE_COLOR)
        )
        time.sleep(0.5)  # Задержка на анимацию раскрытия палитры

        # 3. Кликаем по кнопке элемента цвета
        try:
            color_btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", color_btn)

        print("[TRANSACTIONS MODAL] Первый цвет иконки типа расхода успешно выбран.")

        # 5. Сохранение типа
        save_btn = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.SAVE_TYPE_BTN))
        save_btn.click()
    
        # Возврат в форму транзакции
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(self.MODAL_TITLE))