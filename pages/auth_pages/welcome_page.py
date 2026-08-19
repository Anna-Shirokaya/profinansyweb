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