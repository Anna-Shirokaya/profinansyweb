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

        self.BTN_VK = (By.CSS_SELECTOR, "form + div button")
        self.BTN_YANDEX = (By.CSS_SELECTOR, "form + div > div > div")
        self.BTN_MAX = (By.CSS_SELECTOR, "form + div > div > button:nth-child(3)")
        self.BTN_TG = (By.CSS_SELECTOR, "form + div > div > button:nth-child(4)")

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
        # 1. Ждем и кликаем по кнопке соцсети
        btn = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(locator))
        btn.click()
        
        # 2. Ждем, пока URL в ТЕКУЩЕЙ вкладке поменяется на нужный (например, id.vk.ru)
        WebDriverWait(self.driver, 10).until(EC.url_contains(expected_url_part))
        
        # 3. Сохраняем новый URL в переменную
        current_url = self.driver.current_url
        
        # 4. Возвращаемся назад на страницу регистрации (чтобы тест мог продолжить работу)
        self.driver.back()
        
        # 5. Отдаем сохраненный URL в сам тест для финальной проверки
        return current_url

    def verify_yandex_button_opens_new_window(self, expected_url_part):
        original_window = self.driver.current_window_handle
        
        # 1. Находим iframe Яндекса и "заходим" внутрь него
        iframe = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#yandexButtonContainer iframe"))
        )
        self.driver.switch_to.frame(iframe)
        
        # 2. Находим кнопку УЖЕ ВНУТРИ фрейма и кликаем по ней
        btn_inside = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button"))
        )
        btn_inside.click()
        
        # 3. ВАЖНО: "выходим" из фрейма обратно на главную страницу сайта
        self.driver.switch_to.default_content()
        
        # 4. Ждем появления второго окна/вкладки
        WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(2))
        
        # 5. Переключаемся на новое окно Яндекса
        for window_handle in self.driver.window_handles:
            if window_handle != original_window:
                self.driver.switch_to.window(window_handle)
                break
                
        # 6. Ждем URL и сохраняем его
        WebDriverWait(self.driver, 10).until(EC.url_contains(expected_url_part))
        new_window_url = self.driver.current_url
        
        # 7. Закрываем вкладку Яндекса и возвращаемся в исходное окно
        self.driver.close()
        self.driver.switch_to.window(original_window)
        
        return new_window_url

    def verify_social_button_opens_new_window(self, locator, expected_url_part):
        original_window = self.driver.current_window_handle
        
        # 1. Находим кнопку и кликаем по ней (используем надежный JS-клик)
        btn = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(locator))
        self.driver.execute_script("arguments[0].click();", btn)
        
        # 2. Ждем появления второй вкладки
        WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(2))
        
        # 3. Переключаемся на новую вкладку
        for window_handle in self.driver.window_handles:
            if window_handle != original_window:
                self.driver.switch_to.window(window_handle)
                break
                
        # 4. Ждем нужный URL и сохраняем его
        WebDriverWait(self.driver, 10).until(EC.url_contains(expected_url_part))
        new_window_url = self.driver.current_url
        
        # 5. Закрываем вкладку Макса/Телеграма и возвращаемся на главную
        self.driver.close()
        self.driver.switch_to.window(original_window)
        
        return new_window_url