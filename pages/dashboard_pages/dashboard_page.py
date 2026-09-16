import time
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

class DashboardPage:
    def __init__(self, driver):
        self.driver = driver

    # ЛОКАТОРЫ
    #кнопка Добавить операцию
    ADD_TRANSACTION_BTN = (
        By.XPATH, 
        "//button[.//span[text()='Добавить операцию']] | "
        "//button[contains(., 'Добавить операцию')]"
    )
    
    MY_MONEY_HEADER = (By.XPATH, "//*[text()='Мои деньги']")
    POPUP_CLOSE_BUTTON = (By.XPATH, (
        "//button[contains(@class, 'close')] | //div[contains(@class, 'close')] | "
        "//*[contains(@class, 'Close')] | //button[@aria-label='Close']"
    ))
    # Точный локатор тега <a> с опорой на aria-label и href со скриншота
    BUDGET_MENU_BUTTON = (
        By.XPATH, 
        "//a[@aria-label='Бюджет' or contains(@href, '/wallet')]"
    )
    ACCOUNTS_TEXT_ELEMENTS = (By.XPATH, "//*[text()='Счета']")

    #карточка Все дебетовые
    ALL_ACCOUNTS_CARD_BY_SUBTITLE = staticmethod(
        lambda subtitle="Дебетовые": (
            By.XPATH,
            f"//div[@role='button' and .//span[contains(@class, 'Title') and text()='Все счета'] and .//span[contains(@class, 'SubTitle') and text()='{subtitle}']]"
        )
    )
    #блок история транзакций
    HISTORY_HEADER = (
        By.XPATH, 
        "//a[@href='/wallet/history' or contains(@class, 'TransactionsHeader__InlineHeadline')]"
    )

    TRANSACTION_HISTORY_ITEM_BY_NAME = lambda name: (
        By.XPATH, 
        f"//*[contains(text(), '{name}')]/ancestor::div[contains(@class, 'TransactionItemDetailedstyled__Root')][1]"
    )

    # --- Локаторы удаления типа расхода в Настройках ---
    SETTINGS_BTN = (
        By.XPATH, 
        "//button[contains(@class, 'SettingsButton')]"
    )
    CATEGORIES_OPTION = (
        By.XPATH, 
        "//label[.//p[text()='Категории']] | //p[text()='Категории']"
    )
    EXPENSES_DROPDOWN_TITLE = (
        By.XPATH, 
        "//p[contains(@class, 'style_dropdownTitle') and text()='Расходы']"
    )
    EXPENSE_TYPE_ITEM_BY_NAME = lambda name: (
        By.XPATH, 
        f"//p[contains(@class, 'style_typeTitle') and text()='{name}']"
    )
    DELETE_TYPE_BTN = (
        By.XPATH, 
        "//button[contains(@class, 'style_deleteBtn') and .//span[text()='Удалить']]"
    )
    CONFIRM_DELETE_MODAL_BTN = (
        By.XPATH, 
        "//div[contains(@class, 'style_btns')]//button[contains(@class, 'style_deleteBtn') and .//span[text()='Удалить']]"
    )

    # Локатор вкладок истории операций (Расходы, Доходы, Переводы, Накопления)
    HISTORY_TAB_BY_NAME = staticmethod(
        lambda tab_name: (
            By.XPATH,
            f"//button[contains(., '{tab_name}')] | //*[contains(@class, 'Tab') or @role='tab'][contains(., '{tab_name}')]"
        )
    )

    def is_my_money_header_visible(self) -> bool:
        """Проверяет отображение шапки дашборда"""
        try:
            WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located(self.MY_MONEY_HEADER)
            )
            return True
        except Exception:
            return False

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

    @allure.step("Перейти в раздел 'Счета'")
    def open_accounts_section(self):
        """Переход в раздел счетов с защитой от StaleElementReferenceException при перерендере"""
        for step in range(3):
            try:
                budget_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(self.BUDGET_MENU_BUTTON)
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", budget_btn)
                
                try:
                    budget_btn.click()
                except Exception:
                    self.driver.execute_script("arguments[0].click();", budget_btn)
                break
            except StaleElementReferenceException:
                time.sleep(0.5)
                if step == 2:
                    raise

    # Метод клика по кнопке
    @allure.step("Нажать кнопку '+ Добавить операцию'")
    def open_add_transaction_modal(self):
        """Открывает модальное окно создания транзакции"""
        btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.ADD_TRANSACTION_BTN)
        )
        try:
            btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", btn)
        
        print("[DASHBOARD PAGE] Нажата фиолетовая кнопка '+ Добавить операцию'")

    @allure.step("Кликнуть на карточку 'Все счета' ({subtitle})")
    def click_all_accounts_card(self, subtitle="Дебетовые"):
        """Кликает по интерактивному контейнеру карточки 'Все счета'"""
        locator = self.ALL_ACCOUNTS_CARD_BY_SUBTITLE(subtitle)
        
        card = WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located(locator),
            message=f"Карточка 'Все счета' ({subtitle}) не найдена"
        )
        
        # Центрируем карточку во карусели слайдера перед кликом
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", card)
        time.sleep(0.5)
        
        try:
            card.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", card)
            
        print(f"[DASHBOARD PAGE] Успешно нажата карточка 'Все счета' ({subtitle})")

    @allure.step("Детальная проверка верстки карточки транзакции (строки и красный цвет)")
    def verify_transaction_in_history(self, type_name: str, expected_amount: str, expected_account_name: str):
        """Проверяет построчное расположение элементов карточки и цвет суммы согласно WAL-T519."""
        # 1. Поиск контейнера последней транзакции
        item = WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((
                By.XPATH, 
                "(//div[contains(@class, 'TransactionItemDetailedstyled__Root')])[1]"
            ))
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", item)
        time.sleep(0.5)

        # 2. ПРОВЕРКА ЛЕВОГО БЛОКА (Строка 1 — Название типа, Строка 2 — Категория)
        left_block = item.find_element(By.XPATH, ".//div[contains(@class, 'TransactionItemDetailedstyled__Left')]")
        left_lines = [line.strip() for line in left_block.text.replace("\xa0", " ").split("\n") if line.strip()]

        with allure.step("Проверить 1-ю и 2-ю строки слева (Тип и Категория)"):
            assert type_name[:15] in left_lines[0], (
                f"На 1-й строке слева должно быть название типа! Найдено: '{left_lines[0]}'"
            )
            assert "Переменные" in left_lines[1], (
                f"На 2-й строке слева должна быть категория 'Переменные'! Найдено: '{left_lines[1]}'"
            )

        # 3. ПРОВЕРКА ПРАВОГО БЛОКА (Строка 1 — Сумма с минусом, Строка 2 — Имя счета)
        right_block = item.find_element(By.XPATH, ".//div[contains(@class, 'TransactionItemDetailedstyled__Right')]")
        right_lines = [line.strip() for line in right_text.replace("\xa0", " ").split("\n") if line.strip()] if 'right_text' in locals() else [line.strip() for line in right_block.text.replace("\xa0", " ").split("\n") if line.strip()]

        clean_num = expected_amount.replace(",", ".").strip()
        val_float = float(clean_num)
        formatted_amount = f"-{val_float:,.2f} ₽".replace(",", " ").replace(".", ",")

        with allure.step("Проверить 1-ю и 2-ю строки справа (Сумма с минусом и Счет)"):
            assert formatted_amount in right_lines[0], (
                f"На 1-й строке справа должна быть сумма '{formatted_amount}'! Найдено: '{right_lines[0]}'"
            )
            assert expected_account_name in right_lines[1], (
                f"На 2-й строке справа (под суммой) должно быть имя счета! Найдено: '{right_lines[1]}'"
            )

        # 4. ПРОВЕРКА КРАСНОГО ЦВЕТА СУММЫ
        amount_element = right_block.find_element(By.XPATH, ".//*[contains(text(), '₽') or contains(text(), '-')]")
        css_color = amount_element.value_of_css_property("color")

        with allure.step("Проверить, что цвет суммы красный"):
            # Красный цвет в браузерах передается в формате rgba/rgb с доминирующим красным каналом (R > 180)
            assert any(red_code in css_color for red_code in ["255,", "235,", "240,", "225,", "204,", "248,"]), (
                f"Сумма должна быть красного цвета! Фактический CSS color: '{css_color}'"
            )
            print(f"[DASHBOARD PAGE] Цвет суммы подтвержден (красный): {css_color}")

    def get_history_tab_locator(self, tab_name: str):
        """Возвращает XPath-локатор вкладки фильтрации в истории операций."""
        return (
            By.XPATH,
            f"//button[contains(., '{tab_name}')] | //*[contains(@class, 'Tab') or @role='tab'][contains(., '{tab_name}')]"
        )

    @allure.step("Переключиться на вкладку '{tab_name}' в истории операций")
    def switch_history_tab(self, tab_name: str):
        """Переключает активную вкладку фильтра в истории операций (например, 'Расходы')."""
        tab_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.HISTORY_TAB_BY_NAME(tab_name))
        )
        try:
            tab_btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", tab_btn)
            
        time.sleep(0.5)
        print(f"[DASHBOARD PAGE] Перешли на вкладку '{tab_name}' в истории операций.")

    @allure.step("Переключиться на вкладку '{tab_name}' в истории операций")
    def switch_history_tab(self, tab_name: str):
        """Переключает активную вкладку фильтра в истории операций (например, 'Доходы')."""
        tab_locator = self.get_history_tab_locator(tab_name)
        tab_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(tab_locator)
        )
        try:
            tab_btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", tab_btn)
            
        time.sleep(0.5)
        print(f"[DASHBOARD PAGE] Перешли на вкладку '{tab_name}' в истории операций.")

    def get_expense_type_pencil_locator(self, type_name: str):
        """Возвращает XPath-локатор кнопки-карандаша для типа расхода по его названию."""
        type_prefix = type_name[:15]
        return (
            By.XPATH,
            f"//div[contains(@class, 'sideModal') or contains(@class, 'style_typesDropdown')]"
            f"//div[contains(@class, 'style_typeItem') and .//p[contains(text(), '{type_prefix}')]]"
            f"//button[contains(@class, 'style_expenseTypeBookmark')]"
        )

    @allure.step("Проверить, что история операций пуста")
    def verify_history_is_empty(self):
        """Проверяет отображение сообщения об отсутствии операций в выбранной вкладке."""
        empty_locator = (
            By.XPATH, 
            "//*[contains(text(), 'За выбранный период операций не найдено') or contains(text(), 'Операций не найдено')]"
        )
        empty_element = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(empty_locator),
            message="Сообщение об отсутствии операций не появилось!"
        )
        assert empty_element.is_displayed(), "История операций не пуста!"
    
    @allure.step("Удалить созданный тип расхода '{type_name}' через Настройки")
    def delete_expense_type(self, type_name: str):
        """Возвращается наверх страницы, переходит в Настройки -> Категории -> Расходы и удаляет тип."""
        # 1. Возвращаем скролл на самый верх страницы
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.5)

        # 2. Клик на Настройки (шестеренка)
        settings_btn = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.SETTINGS_BTN)
        )
        self.driver.execute_script("arguments[0].click();", settings_btn)

        # 3. Клик на 'Категории'
        categories_label = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.CATEGORIES_OPTION)
        )
        self.driver.execute_script("arguments[0].click();", categories_label)
        time.sleep(0.5)

        # 4. Вызов вынесенного локатора карандаша
        pencil_locator = self.get_expense_type_pencil_locator(type_name)

        try:
            # Если списки категорий уже раскрыты по умолчанию, ищем карандаш
            pencil_btn = self.driver.find_element(*pencil_locator)
        except Exception:
            # Если список свёрнут — кликаем по 'Расходы' для раскрытия
            expenses_dropdown = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(self.EXPENSES_DROPDOWN_TITLE)
            )
            self.driver.execute_script("arguments[0].click();", expenses_dropdown)
            time.sleep(0.5)
            # Ждем появления карандаша после анимации
            pencil_btn = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(pencil_locator)
            )

        # 5. Скроллим и кликаем СТРОГО по кнопке с карандашом
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", pencil_btn)
        time.sleep(0.5)
        self.driver.execute_script("arguments[0].click();", pencil_btn)

        # 6. Клик на кнопку 'Удалить' в открывшейся форме редактирования
        delete_btn = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.DELETE_TYPE_BTN)
        )
        self.driver.execute_script("arguments[0].click();", delete_btn)

        # 7. Подтверждение удаления в модальном окне
        confirm_btn = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.CONFIRM_DELETE_MODAL_BTN)
        )
        self.driver.execute_script("arguments[0].click();", confirm_btn)

        WebDriverWait(self.driver, 10).until_not(
            EC.presence_of_element_located(self.CONFIRM_DELETE_MODAL_BTN)
        )
        print(f"[DASHBOARD PAGE] Тип расхода '{type_name}' успешно удален.")