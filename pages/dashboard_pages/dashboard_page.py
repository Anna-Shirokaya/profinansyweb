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