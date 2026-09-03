import time
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
        self.SOURCE_ACCOUNT_TRIGGER = (
            By.XPATH, 
            "//input[@name='expenseWallet'] | "
            "//div[contains(@class, 'InputField-root') and .//label[contains(., 'Откуда')]]//input"
        )
        
        self.DESTINATION_ACCOUNT_TRIGGER = (
            By.XPATH, 
            "//input[@name='accumulationWallet'] | "
            "//div[contains(@class, 'InputField-root') and .//label[contains(., 'Куда')]]//input"
        )
        
        self.ACCUMULATION_TAB = (
            By.XPATH, 
            "//div[contains(@class, 'transaction-swiper-type') and .//p[text()='Накопления']]"
        )

        self.AMOUNT_INPUT = (
            By.XPATH, 
            "//input[@placeholder='0'] | "
            "//*[contains(text(), 'Сумма')]/following::input[1]"
        )

        self.SUBMIT_BUTTON = (
            By.XPATH, 
            "//button[./span[text()='Создать']] | "
            "//button[contains(., 'Создать')] | "
            "//div[contains(@class, 'sidebarSlides')]//button"
        )

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

    @allure.step("Нажать кнопку 'Создать'")
    def click_submit_button(self):
        btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.SUBMIT_BUTTON)
        )
        try:
            btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", btn)
        time.sleep(1)

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