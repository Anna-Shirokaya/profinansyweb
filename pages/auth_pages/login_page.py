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