import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

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
        """Универсальное закрытие промо-окон через ESC и клик по крестику/подложке"""
        # 1. Быстрый сброс модалок через клавишу ESC
        try:
            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        except Exception:
            pass

        # 2. Если модалка осталась — ищем крестик или кликаем по подложке
        locators = [
            (By.XPATH, "//button[contains(@class, 'close')] | //div[contains(@class, 'close')]"),
            (By.XPATH, "//*[contains(@class, 'modal')]//button"),
            (By.XPATH, "//div[contains(@class, 'gLWLmN')]")  # Клик по подложке из вашей ошибки
        ]
        
        for locator in locators:
            try:
                close_btn = WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located(locator)
                )
                self.driver.execute_script("arguments[0].click();", close_btn)
                print("[PAGE] Промо-окно успешно закрыто.")
                break
            except Exception:
                continue

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
        """Переход в раздел счетов через клик по меню с сохранением авторизации"""
        # 1. Принудительно удаляем из DOM любые прозрачные подложки и модалки, блокирующие клик
        self.driver.execute_script("""
            var overlays = document.querySelectorAll("div[class*='gLWLmN'], div[class*='modal'], [class*='overlay']");
            overlays.forEach(function(el) { el.remove(); });
        """)

        # 2. Ждем появление кнопки "Бюджет" в DOM
        budget_btn = WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located(self.BUDGET_MENU_BUTTON)
        )

        # 3. Прокручиваем к ней и делаем чистый клик без перезагрузки страницы
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", budget_btn)
        
        try:
            budget_btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", budget_btn)