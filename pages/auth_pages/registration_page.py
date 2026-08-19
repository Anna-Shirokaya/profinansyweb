from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class RegistrationPage:
    def __init__(self, driver):
        self.driver = driver
        
        # Используем NAME вместо XPATH по placeholder для максимальной точности
        self.INPUT_EMAIL = (By.NAME, "email") 
        self.CHECKBOX_POLICY = (By.XPATH, "//input[@name='personal_data']") 
        self.CHECKBOX_PROMO = (By.XPATH, "//input[@name='advertising']")   
        self.BTN_ONE_STEP_LEFT = (By.XPATH, "//button[contains(., 'Остался один шаг')]")
        self.ERROR_MESSAGE_EMAIL = (By.ID, "email-error")

        # ДОПОЛНИТЕЛЬНЫЕ ЛОКАТОРЫ (Для шага ввода пароля и завершения регистрации)
        self.INPUT_PASSWORD = (By.XPATH, "//input[@name='password']")
        self.INPUT_PASSWORD_REPEAT = (By.XPATH, "//input[@name='repeat_password']")

        self.BTN_REGISTER = (By.XPATH, "//button[contains(., 'Зарегистрироваться')]")
        self.CAPTCHA_REQ_ERROR = (By.XPATH, "//span[@role='alert' and contains(@class, 'error-text') and contains(text(), 'Обязательное поле')]")
        self.CAPTCHA_IFRAME = (By.XPATH, "//iframe[contains(@title, 'reCAPTCHA') or contains(@src, 'recaptcha')]")
        self.CAPTCHA_CHECKBOX = (By.XPATH, "//div[@class='recaptcha-checkbox-border']")
        self.CAPTCHA_CHALLENGE_IFRAME = (By.XPATH, "//iframe[contains(@src, 'bframe') or contains(@title, 'recaptcha')]")
        self.USED_EMAIL_ERROR_TEXT = (By.XPATH, "//*[contains(text(), 'пользователь уже существует') or contains(@class, 'error')]") # Уточни текст по факту
        self.BTN_ANOTHER_EMAIL = (By.XPATH, "//button[contains(., 'Ввести другой email')]")
        
        
        # Локаторы куки и промо (как на WelcomePage)
        self.COOKIE_ACCEPT_BUTTON = (By.XPATH, "//*[text()='Понятно']")
        self.PROMO_CLOSE_BUTTON = (By.XPATH, "//button[contains(@class, 'close')] | //div[contains(@class, 'close')]")

        # УНИВЕРСАЛЬНЫЕ ЛОКАТОРЫ СОЦСЕТЕЙ (Регистронезависимый поиск + fallback по структуре)
        SOCIAL_BOX = (
            "//span[contains(translate(text(), 'ИЛИ', 'или'), 'или')]/following-sibling::div "
            "| //form//div[count(button)+count(div)>=4]"
        )

        self.BTN_VK = (By.XPATH, f"({SOCIAL_BOX})[1]/*[1]")
        self.BTN_YANDEX = (By.XPATH, f"({SOCIAL_BOX})[1]/*[2]")
        self.BTN_MAX = (By.XPATH, f"({SOCIAL_BOX})[1]/*[3]")
        self.BTN_TELEGRAM = (By.XPATH, f"({SOCIAL_BOX})[1]/*[4]")

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
        """Прокликивает чек-боксы согласий (используем JS-клик для скрытых нативных инпутов)"""
        # Ждем физического присутствия элемента в HTML, а не его визуальной отрисовки
        policy_checkbox = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.CHECKBOX_POLICY)
        )
        self.driver.execute_script("arguments[0].click();", policy_checkbox)
        print("\n[REGISTRATION PAGE] Выбран чек-бокс 'Согласен с политикой'")
        
        promo_checkbox = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.CHECKBOX_PROMO)
        )
        self.driver.execute_script("arguments[0].click();", promo_checkbox)
        print("[REGISTRATION PAGE] Выбран чек-бокс 'Рекламная рассылка'")

    def is_one_step_button_enabled(self):
        """Проверяет, активна ли кнопка 'Остался один шаг'"""
        btn = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.BTN_ONE_STEP_LEFT)
        )
        return btn.is_enabled()

    def click_one_step_left(self):
        """Кликает по кнопке 'Остался один шаг' с защитой от перекрытия"""
        btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.BTN_ONE_STEP_LEFT)
        )
        try:
            btn.click()
            print("\n[REGISTRATION PAGE] Нажата кнопка 'Остался один шаг' (обычный клик)")
        except Exception:
            print("\n[REGISTRATION PAGE] Обычный клик перехвачен, используем JS-клик...")
            self.driver.execute_script("arguments[0].click();", btn)

    def get_email_error_text(self):
        """Получает текст ошибки валидации email"""
        error_el = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.ERROR_MESSAGE_EMAIL)
        )
        return error_el.text

    def enter_passwords(self, password):
        """Вводит пароль и подтверждение пароля"""
        pass_el = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.INPUT_PASSWORD)
        )
        pass_el.clear()
        pass_el.send_keys(password)
        
        pass_repeat_el = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.INPUT_PASSWORD_REPEAT)
        )
        pass_repeat_el.clear()
        pass_repeat_el.send_keys(password)

    def click_captcha(self):
        """Кликает по чек-боксу капчи"""
        captcha_el = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.CAPTCHA_CHECKBOX)
        )
        try:
            captcha_el.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", captcha_el)

    def click_register_button(self):
        """Кликает по финальной кнопке 'Зарегистрироваться'"""
        btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.BTN_REGISTER)
        )
        try:
            btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", btn)

    def is_used_email_error_visible(self):
        """Проверяет появление ошибки о занятом email"""
        try:
            error_el = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(self.USED_EMAIL_ERROR_TEXT)
            )
            return error_el.is_displayed()
        except TimeoutException:
            return False

    # === МЕТОДЫ ДЛЯ ВТОРОГО ШАГА РЕГИСТРАЦИИ (WAL-T442) ===

    def is_register_button_enabled(self):
        """Проверяет, активна ли финальная кнопка регистрации"""
        btn = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.BTN_REGISTER)
        )
        return btn.is_enabled()

    def click_register_button(self):
        """Кликает по кнопке 'Зарегистрироваться' с защитой от перекрытия"""
        btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.BTN_REGISTER)
        )
        try:
            btn.click()
            print("\n[REGISTRATION PAGE] Нажата кнопка 'Зарегистрироваться'")
        except Exception:
            self.driver.execute_script("arguments[0].click();", btn)

    def is_captcha_error_displayed(self):
        """Проверяет появление ошибки обязательности капчи"""
        return WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.CAPTCHA_REQ_ERROR)
        ).is_displayed()

    def click_another_email_button(self):
        """Кликает по кнопке возврата 'Ввести другой email'"""
        btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.BTN_ANOTHER_EMAIL)
        )
        try:
            btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", btn)
            
    def is_email_input_displayed(self):
        """Проверка возврата на первый шаг (видимость поля email)"""
        return WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.INPUT_EMAIL)
        ).is_displayed()

    def click_captcha(self):
        """Клик по чек-боксу Google reCAPTCHA с обработкой появления картинок"""
        import pytest
        from selenium.common.exceptions import TimeoutException
        import time
        
        # 1. Заходим в основной фрейм капчи и кликаем чек-бокс
        iframe = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.CAPTCHA_IFRAME)
        )
        self.driver.switch_to.frame(iframe)
        
        try:
            captcha_box = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(self.CAPTCHA_CHECKBOX)
            )
            captcha_box.click()
            print("\n[REGISTRATION PAGE] Успешно кликнули по чек-боксу reCAPTCHA")
            
            time.sleep(2) # Ждем, пока Гугл "подумает"
        finally:
            # Обязательно возвращаемся в основной документ
            self.driver.switch_to.default_content()
            
        # 2. Проверяем, не выкинул ли Гугл окно с картинками (challenge)
        try:
            # Ждем всего 3 секунды, чтобы не затягивать тест, если картинок нет
            challenge = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(self.CAPTCHA_CHALLENGE_IFRAME)
            )
            if challenge.is_displayed():
                # Если фрейм с автобусами появился — элегантно прерываем тест
                pytest.skip("Гугл запросил решение капчи с картинками. Дальнейшее выполнение теста невозможно (anti-bot защита).")
        except TimeoutException:
            # Если через 3 секунды окно не появилось — Гугл пустил нас просто по галочке!
            print("\n[REGISTRATION PAGE] Капча пройдена без картинок, продолжаем тест.")

    def verify_social_button_opens_url(self, locator, expected_url_part):
        """
        Кликает по соцсети реальным кликом мыши (ActionChains),
        проверяет URL открывшейся страницы и возвращается на форму.
        """
        import time
        from selenium.webdriver.common.action_chains import ActionChains
        from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

        main_window = self.driver.current_window_handle
        initial_handles_count = len(self.driver.window_handles)

        # 1. Ждем загрузки формы
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.INPUT_EMAIL)
        )

        # 2. Ищем элемент и делаем РЕАЛЬНЫЙ клик мыши через ActionChains
        end_time = time.time() + 10
        while True:
            try:
                target_element = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(locator)
                )
                
                # Скроллим к элементу
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target_element)
                time.sleep(0.5)

                # Физический клик мыши по центру элемента
                actions = ActionChains(self.driver)
                actions.move_to_element(target_element).click().perform()
                print(f"\n[REGISTRATION PAGE] Физический клик по элементу: {locator}")
                break
            except (StaleElementReferenceException, Exception):
                if time.time() > end_time:
                    # Запасной JS-клик, если ActionChains не сработал
                    target_element = self.driver.find_element(*locator)
                    self.driver.execute_script("arguments[0].click();", target_element)
                    break
                time.sleep(0.5)

        # 3. Ждем открытия нового окна или редиректа в текущем
        try:
            WebDriverWait(self.driver, 10).until(
                lambda d: len(d.window_handles) > initial_handles_count or expected_url_part in d.current_url
            )
        except TimeoutException:
            time.sleep(2)

        # 4. Проверяем URL и возвращаемся назад
        if len(self.driver.window_handles) > initial_handles_count:
            new_window = [handle for handle in self.driver.window_handles if handle != main_window][0]
            self.driver.switch_to.window(new_window)
            
            WebDriverWait(self.driver, 10).until(EC.url_contains(expected_url_part))
            current_url = self.driver.current_url

            self.driver.close()
            self.driver.switch_to.window(main_window)
        else:
            WebDriverWait(self.driver, 10).until(EC.url_contains(expected_url_part))
            current_url = self.driver.current_url

            self.driver.back()
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(self.INPUT_EMAIL))

        return current_url