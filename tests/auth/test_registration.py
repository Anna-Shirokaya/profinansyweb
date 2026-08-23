import pytest
from pages.auth_pages.welcome_page import WelcomePage
from pages.auth_pages.registration_page import RegistrationPage

class TestWebRegistration:
    
    def test_wal_t301_registration_flow(self, driver):
        """WAL-T301: Регистрация через почту (Позитивный сценарий)"""
        welcome_page = WelcomePage(driver)
        registration_page = RegistrationPage(driver)
        
        # 1 Step: Перейти на страницу welcome
        welcome_page.open()
        
        # 2 Step: Тап на "Регистрация"
        welcome_page.click_register_button()
        
        # 3 Step: Ввести валидный email
        registration_page.enter_email("new_qa_user@mails.org")
        
        # Expected: Пока не выбраны оба чек-бокса кнопка "Остался один шаг" задизайблена
        assert not registration_page.is_one_step_button_enabled(), "Кнопка активна без чек-боксов!"
        
        # 4 Step: Выбрать оба чек-бокса
        registration_page.select_all_checkboxes()
        
        # Expected: Кнопка "Остался один шаг" активна
        assert registration_page.is_one_step_button_enabled(), "Кнопка не стала активной!"
        
        # 5 Step: Клик на кнопку
        registration_page.click_one_step_left()

    def test_wal_t302_email_with_leading_space(self, driver):
        """WAL-T302: Регистрация через почту: ввод адреса почты с пробелом спереди"""
        registration_page = RegistrationPage(driver)

        # 1 Step: Перейти на страницу, Ввести адрес почты с пробелом спереди
        registration_page.open_directly()
        registration_page.enter_email(" anna1038@gmail.com")

        # Expected 1: Ошибка не отображается (переходим сразу к следующему шагу)
        # 2 Step: Установить 2 радио баттона (чек-бокса)
        registration_page.select_all_checkboxes()

        # Expected 2: Кнопка "Остался один шаг" становится активной
        assert registration_page.is_one_step_button_enabled(), "Кнопка 'Остался один шаг' не стала активной!"

        # 3 Step: Клик на кнопку "Остался один шаг"
        registration_page.click_one_step_left()

        # Expected 3: Отображается форма для ввода пароля
        # Используем явное ожидание появления поля пароля, чтобы подтвердить переход
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        password_field = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(registration_page.INPUT_PASSWORD)
        )
        assert password_field.is_displayed(), "Форма ввода пароля не отобразилась!"
        print("\n[ТЕСТ] WAL-T302 пройден: Пробел в начале email успешно обработан системой.")

    def test_wal_t304_email_without_at_symbol(self, driver):
        """WAL-T304: Регистрация через почту: ввод адреса почты без @"""
        registration_page = RegistrationPage(driver)

        # 1 Step: Перейти на страницу регистрации
        registration_page.open_directly()
        
        # Ввести адрес почты без @
        registration_page.enter_email("anna1038yandex.ru")

        # Выбрать оба радио-баттона (согласно шагам из ручного тест-кейса)
        registration_page.select_all_checkboxes()
        
        # Клик на кнопку "Остался один шаг"
        registration_page.click_one_step_left()

        # Expected: Отображается ошибка валидации e-mail
        error_text = registration_page.get_email_error_text()
        assert error_text == "Некорректный e-mail", f"Ожидалась ошибка 'Некорректный e-mail', но получили: '{error_text}'"
        print("\n[ТЕСТ] WAL-T304 пройден: Ошибка отсутствия @ отобразилась корректно.")

    def test_wal_t303_empty_email(self, driver):
        """WAL-T303: Регистрация через почту: ничего не вводить в строку для ввода почты"""
        registration_page = RegistrationPage(driver)
        
        # 1 Step: Перейти на страницу, ничего не вводить, выбрать оба чек бокса
        registration_page.open_directly()
        registration_page.select_all_checkboxes()
        
        # Expected: Кнопка "Остался один шаг" задизейблена
        assert not registration_page.is_one_step_button_enabled(), "Кнопка 'Остался один шаг' должна быть неактивна при пустом e-mail"
        print("\n[ТЕСТ] WAL-T303 пройден: Кнопка заблокирована при пустом email.")

    def test_wal_t305_cyrillic_email(self, driver):
        """WAL-T305: Регистрация через почту: ввод адреса почты, один знак - кириллица"""
        registration_page = RegistrationPage(driver)

        # 1 Step: Перейти на страницу, ввести email с кириллицей
        registration_page.open_directly()
        invalid_email = "annа1038@yandex.ru" # 'а' — кириллица
        registration_page.enter_email(invalid_email)

        # ТРИГГЕР ВАЛИДАЦИИ: Прокликиваем чек-боксы и жмем кнопку
        registration_page.select_all_checkboxes()
        registration_page.click_one_step_left()

        # Expected: Отображается ошибка (берем точный текст по ID)
        error_text = registration_page.get_email_error_text()
        assert error_text == "Некорректный e-mail", f"Ожидалась ошибка 'Некорректный e-mail', но получили: '{error_text}'"
        print("\n[ТЕСТ] WAL-T305 пройден: Кириллица успешно заблокирована.")

    def test_wal_t442_already_used_email(self, driver):
        """WAL-T442: Регистрация через уже использованную почту"""
        registration_page = RegistrationPage(driver)

        # 1-2 Step: Перейти на страницу, ввести занятый email и отметить чек-боксы
        registration_page.open_directly()
        used_email = "anna1038@yandex.ru"
        registration_page.enter_email(used_email)
        registration_page.select_all_checkboxes()

        # Expected 2: Кнопка "Остался один шаг" становится активной
        assert registration_page.is_one_step_button_enabled(), "Кнопка 'Остался один шаг' не стала активной!"

        # 3 Step: Тап на кнопку
        registration_page.click_one_step_left()

        # Expected 3: Отображается форма для ввода пароля (ожидаем само поле)
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located(registration_page.INPUT_PASSWORD))

        # 4 Step: Два раза ввести валидный пароль
        registration_page.enter_passwords("Anna0412@")

        # Expected 4: Появляется капча, кнопка становится активной
        assert registration_page.is_register_button_enabled(), "Кнопка 'Зарегистрироваться' не активна после ввода паролей!"

        # 5 Step: Тап на "Зарегистрироваться" (капча специально не прожата)
        registration_page.click_register_button()

        # Expected 5: Показано сообщение, что капча - обязательное поле
        assert registration_page.is_captcha_error_displayed(), "Отсутствует валидация обязательности капчи!"

        # 6 Step: Отметить капчу и тап на "Зарегистрироваться"
        # Примечание: на тестовых контурах капчу часто мокают/отключают. Если тут используется нативная Yandex SmartCaptcha или ReCaptcha, возможно, потребуется JS-инъекция или отключение флагами окружения.
        registration_page.click_captcha()
        registration_page.click_register_button()

        # Expected 6: Показано сообщение об ошибке (уже зарегистрирован)
        # Убеждаемся, что появилась кнопка "Ввести другой email" (как индикатор окна ошибки)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located(registration_page.BTN_ANOTHER_EMAIL))

        # 7 Step: Тап на "Ввести другой email"
        registration_page.click_another_email_button()

        # Expected 7: Отображается страница регистрации
        assert registration_page.is_email_input_displayed(), "Не произошел возврат на первый шаг регистрации!"
        
        print("\n[ТЕСТ] WAL-T442 пройден: Обработка дубликата email и валидация капчи работают корректно.")

    def test_wal_t148_initial_registration_page(self, driver):
        """WAL-T148: Начальная страница регистрации"""
        registration_page = RegistrationPage(driver)

        # 1 Step: Перейти на страницу регистрации
        registration_page.open_directly()

        # Expected: Открывается начальная страница регистрации (проверяем UI элементы формы)
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        # Ждем появления поля E-mail как индикатора загрузки формы
        email_field = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(registration_page.INPUT_EMAIL)
        )
        assert email_field.is_displayed(), "Поле ввода E-mail не отображается на начальной странице!"

        # Проверяем наличие главной кнопки
        btn = driver.find_element(*registration_page.BTN_ONE_STEP_LEFT)
        assert btn.is_displayed(), "Кнопка 'Остался один шаг' не отображается!"

        print("\n[ТЕСТ] WAL-T148 пройден: Начальная страница регистрации загружена и элементы формы видны.")

    def test_wal_t232_registration_via_social_networks(self, driver):
        """WAL-T232: Проверка регистрации через соц сети"""
        registration_page = RegistrationPage(driver)

        # 1 Step: Перейти на страницу регистрации
        registration_page.open_directly()

        # 2 Step: Клик на кнопку VK -> Ожидаемый результат: Отображается окно "Вход с помощью VK ID"
        vk_url = registration_page.verify_social_button_opens_url(
            registration_page.BTN_VK, "id.vk.ru"
        )
        assert "vk.com" in vk_url or "id.vk" in vk_url, f"Неверный URL при клике на VK: {vk_url}"
        print("\n[ТЕСТ] WAL-T232 Шаг 2 (VK ID): Окно авторизации успешно открылось.")       

    def test_registration_via_yandex(self, driver):
        """Проверка регистрации через Яндекс (в новом окне)"""
        registration_page = RegistrationPage(driver)
        registration_page.open_directly()
        
        # Используем новый метод специально для Яндекса
        yandex_url = registration_page.verify_yandex_button_opens_new_window("yandex")
        
        assert "yandex" in yandex_url, f"Неверный URL при клике на Яндекс: {yandex_url}"
        print("\n[ТЕСТ] Яндекс: Окно авторизации успешно открылось.")

    def test_registration_via_max(self, driver):
        """Проверка регистрации через Макс (в новой вкладке)"""
        registration_page = RegistrationPage(driver)
        registration_page.open_directly()
        
        # Используем метод для нового окна/вкладки и ждем "max.ru"
        max_url = registration_page.verify_social_button_opens_new_window(
            registration_page.BTN_MAX, "max.ru" 
        )
        assert "max.ru" in max_url, f"Неверный URL при клике на Макс: {max_url}"
        print("\n[ТЕСТ] Макс: Вкладка авторизации успешно открылась.")


    def test_registration_via_tg(self, driver):
        """Проверка регистрации через Telegram"""
        registration_page = RegistrationPage(driver)
        registration_page.open_directly()
        
        # Вызываем правильный метод, умеющий работать со вторым окном
        tg_url = registration_page.verify_social_button_opens_new_window(
            registration_page.BTN_TG, "t.me/"
        )
        assert "t.me/" in tg_url, f"Неверный URL при клике на Telegram: {tg_url}"
        print("\n[ТЕСТ] Telegram: Окно авторизации успешно открылось.")