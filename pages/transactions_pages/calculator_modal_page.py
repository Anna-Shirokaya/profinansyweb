import time
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class CalculatorModalPage:
    def __init__(self, driver):
        self.driver = driver

    # --- СПЕЦИФИЧНЫЕ ЛОКАТОРЫ КАЛЬКУЛЯТОРА ---
    #иконка калькулятора на форме создания транзакции
    CALCULATOR_ICON = (
        By.XPATH, 
        "//span[contains(@class, 'input-icon')]//*[local-name()='svg']"
    )
    CALCULATOR_CONTAINER = (
        By.XPATH, 
        "//div[contains(@class, 'style_calculator') or contains(@class, 'Calculator')] | "
        "//div[contains(@class, 'Popover') and .//button[text()='Применить']]"
    )
    # Дисплей с результатом вычислений
    CALCULATOR_DISPLAY = (
        By.XPATH, 
        "//div[contains(@class, 'FieldCalculatorstyled__ResultBlock') or contains(@class, 'resultBlock')]"
    )
    
    # Кнопка подтверждения значения
    CALCULATOR_APPLY_BTN = (
        By.XPATH, 
        "//button[.//span[text()='Готово'] or contains(., 'Готово') or contains(., 'Применить')]"
    )

    # Кнопка 'AC' / 'C'
    CALCULATOR_AC_BTN = (
        By.XPATH, 
        "//button[contains(@class, 'CalculatorKeyboardstyled__KeyboardButton') and (text()='AC' or text()='C')]"
    )

    # Подсказка над калькулятором
    CALCULATOR_TOOLTIP = (
        By.XPATH, 
        "//div[contains(@class, 'Popover')]//*[contains(text(), 'Рекомендуется')]"
    )

    # Сообщение об ошибке отрицательной суммы
    CALCULATOR_ERROR = (
        By.XPATH, 
        "//p[contains(text(), 'Сумма не может быть отрицательной')]"
    )

    @allure.step("Нажать кнопку 'Готово' (без ожидания закрытия калькулятора)")
    def click_apply_raw(self):
        """Нажимает 'Готово' для проверки валидации ошибок."""
        apply_btn = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable(self.CALCULATOR_APPLY_BTN)
        )
        try:
            apply_btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", apply_btn)

    @allure.step("Получить текст ошибки валидации калькулятора")
    def get_error_text(self) -> str:
        """Возвращает текст красного сообщения об ошибке."""
        err_elem = WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located(self.CALCULATOR_ERROR)
        )
        return err_elem.text.strip()

    @allure.step("Проверить наличие нежелательной подсказки в калькуляторе")
    def is_tooltip_present(self) -> bool:
        """Возвращает True, если на дисплее калькулятора отображается подсказка."""
        try:
            return WebDriverWait(self.driver, 2).until(
                EC.visibility_of_element_located(self.CALCULATOR_TOOLTIP)
            ).is_displayed()
        except Exception:
            return False

    @allure.step("Получить текущее значение с экрана калькулятора")
    def get_display_value(self) -> str:
        """Считывает итоговый результат с последней строки дисплея."""
        display = WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located(self.CALCULATOR_DISPLAY)
        )
        raw_text = display.text.strip()
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        return lines[-1] if lines else ""

    @allure.step("Ввести выражение на калькуляторе с физической клавиатуры: '{expression}'")
    def input_expression_via_keyboard(self, expression: str):
        """Эмулирует ввод цифр и операторов с клавиатуры ПК."""
        active_elem = self.driver.switch_to.active_element
        for char in expression:
            active_elem.send_keys(char)
            time.sleep(0.1)

    def get_calc_key_locator(self, symbol: str):
        """
        Возвращает точный локатор кнопки калькулятора.
        Для цифр использует текст, для операторов-иконок — их позицию относительно цифр в сетке.
        """
        operators_map = {
            '.': "//button[text()=','] | //button[text()='.']",
            ',': "//button[text()=','] | //button[text()='.']",
            '+': "//button[text()='3']/following-sibling::button[2]",
            '-': "//button[text()='3']/following-sibling::button[1]",
            '*': "//button[text()='6']/following-sibling::button[2]",
            'x': "//button[text()='6']/following-sibling::button[2]",
            '/': "//button[text()='6']/following-sibling::button[1]",
            '=': "//button[text()=',']/following-sibling::button[1] | //button[text()='.']/following-sibling::button[1] | //button[normalize-space()='=']",
            '%': "//button[text()='9']/following-sibling::button[2]"
        }

        if symbol in operators_map:
            return (By.XPATH, operators_map[symbol])

        # Для цифр (0-9) и текстовых символов (AC, .)
        return (
            By.XPATH, 
            f"//button[contains(@class, 'CalculatorKeyboardstyled__KeyboardButton') and normalize-space()='{symbol}']"
        )

    @allure.step("Проверить иконку калькулятора и курсор pointer")
    def verify_icon_and_hover(self):
        """Проверяет видимость иконки и курсор мыши (рука/pointer)."""
        icon = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.CALCULATOR_ICON)
        )
        cursor_style = icon.value_of_css_property("cursor")
        assert cursor_style in ["pointer", "hand"], f"Курсор не превращается в руку! Фактический: '{cursor_style}'"
        return icon

    @allure.step("Открыть калькулятор кликом по иконке")
    def open_calculator(self):
        """Открывает поповер калькулятора."""
        icon = self.verify_icon_and_hover()
        try:
            icon.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", icon)

        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.CALCULATOR_CONTAINER)
        )

    @allure.step("Набрать на калькуляторе выражение мышкой: '{expression}'")
    def input_expression_via_mouse(self, expression: str):
        """Нажимает последовательно кнопки калькулятора."""
        for char in expression:
            key_locator = self.get_calc_key_locator(char)
            btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(key_locator),
                message=f"Не найдена кнопка калькулятора '{char}'"
            )
            try:
                btn.click()
            except Exception:
                self.driver.execute_script("arguments[0].click();", btn)
            time.sleep(0.1)

    @allure.step("Нажать кнопку 'AC' в калькуляторе")
    def click_ac(self):
        """Сбрасывает значение кнопкой AC."""
        ac_btn = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable(self.CALCULATOR_AC_BTN)
        )
        try:
            ac_btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", ac_btn)

    @allure.step("Нажать 'Применить' в калькуляторе")
    def apply_result(self):
        """Применяет вычисленный результат и закрывает поповер."""
        apply_btn = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable(self.CALCULATOR_APPLY_BTN)
        )
        try:
            apply_btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", apply_btn)

        WebDriverWait(self.driver, 10).until(
            EC.invisibility_of_element_located(self.CALCULATOR_CONTAINER)
        )
        time.sleep(0.5)