from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException 

class WelcomePage:
    # Локаторы класса
    LOGIN_BUTTON = (By.XPATH, "//*[text()='Вход']")
    REGISTER_BUTTON = (By.XPATH, "//*[text()='Регистрация']")
    COOKIE_ACCEPT_BUTTON = (By.XPATH, "//*[text()='Понятно']")
    PROMO_CLOSE_BUTTON = (By.XPATH, "//button[contains(@class, 'close')] | //div[contains(@class, 'close')]")

    def __init__(self, driver):
        self.driver = driver
        self.url = f"{driver.base_url}/welcome"


    def open(self):
        """Метод для открытия страницы"""
        try:
            self.driver.get(self.url)
        except TimeoutException:
            # Прерываем загрузку фоновых скриптов, если DOM уже готов
            print("\n[WELCOME PAGE] Страница превысила лимит загрузки, останавливаем фоновые метрики...")
            self.driver.execute_script("window.stop();")

        # После открытия проверяем и закрываем куки и промо-модалку
        self.close_cookie_banner_if_exists()
        self.close_promo_modal_if_exists()


    def close_cookie_banner_if_exists(self):
        try:
            # Находим кнопку баннера (используй свой существующий локатор)
            cookie_btn = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located(self.COOKIE_BTN_LOCATOR) # Укажи свой локатор кнопки куки
            )
            # Выполняем гарантированный клик через JS
            self.driver.execute_script("arguments[0].click();", cookie_btn)
        except Exception:
            # Если баннера нет или он не появился — просто идем дальше
            pass


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
        # 1. Ждем появление кнопки "Вход" в DOM
        login_btn = WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located(self.LOGIN_BUTTON)
        )
        
        # 2. Прокручиваем к ней и делаем JS-клик
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", login_btn)
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