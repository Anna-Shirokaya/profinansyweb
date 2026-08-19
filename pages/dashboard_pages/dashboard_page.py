import time
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class DashboardPage:
    def __init__(self, driver):
        self.driver = driver

    # ЛОКАТОРЫ
    MY_MONEY_HEADER = (By.XPATH, "//*[text()='Мои деньги']")
    POPUP_CLOSE_BUTTON = (By.XPATH, (
        "//button[contains(@class, 'close')] | //div[contains(@class, 'close')] | "
        "//*[contains(@class, 'Close')] | //button[@aria-label='Close']"
    ))
    BUDGET_MENU_BUTTON = (By.XPATH, "//nav//a[contains(., 'Бюджет')] | //*[text()='Бюджет']")
    ACCOUNTS_TEXT_ELEMENTS = (By.XPATH, "//*[text()='Счета']")

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
        try:
            # Используем правильно имя: self.BUDGET_MENU_BUTTON
            budget_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(self.BUDGET_MENU_BUTTON)
            )
            self.driver.execute_script("arguments[0].click();", budget_btn)
        except StaleElementReferenceException:
            budget_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(self.BUDGET_MENU_BUTTON)
            )
            self.driver.execute_script("arguments[0].click();", budget_btn)