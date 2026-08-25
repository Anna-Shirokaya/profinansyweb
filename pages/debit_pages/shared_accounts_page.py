import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.debit_pages.accounts_main_page import AccountsMainPage

class SharedAccountsPage(AccountsMainPage):
    # Локаторы шеринга и доступа
    TAB_ACCESS_SHARED = (By.XPATH, "//div[@role='button'][.//p[contains(text(), 'Совместный доступ')]]")
    EMAIL_SHARE_INPUT = (By.XPATH, "//input[@name='email' or @placeholder='Введите адрес электронной почты']")
    BTN_ADD_EMAIL_PLUS = (By.XPATH, "//button[contains(., '+') or contains(@class, 'add-email')]")
    BTN_SAVE_SHARE = (By.XPATH, "//button[contains(., 'Сохранить') or contains(., 'Создать')]")
    
    # Модалка приглашения (шерингополучатель)
    MODAL_INVITE_CONTAINER = (By.XPATH, "//div[contains(text(), 'Вам предоставлен доступ к счёту')]")
    BTN_ACCEPT_INVITE = (By.XPATH, "//button[contains(., 'Принять')]")
    BTN_REJECT_INVITE = (By.XPATH, "//button[contains(., 'Отклонить')]")
    
    # Элементы карточки общего счета
    SHARED_HANDS_ICON = (By.XPATH, "//*[@data-icon='hands' or contains(@class, 'shared-icon')]")
    TOOLTIP_SHARED_INFO = (By.XPATH, "//div[contains(text(), 'Этим счётом с вами поделились')]")
    
    # Меню и модалка отмены отслеживания
    ITEM_UNTRACK = (By.XPATH, "//div[contains(text(), 'Не отслеживать')]")
    MODAL_UNTRACK_CONFIRM = (By.XPATH, "//div[contains(text(), 'Отказаться от доступа к счету?')]")
    BTN_UNTRACK_CONFIRM = (By.XPATH, "//button[contains(., 'Отказаться')]")
    BTN_MODAL_CLOSE_CROSS = (By.XPATH, "//button[contains(@class, 'close') or contains(text(), '×')]")
    
    # Управление доступом шерингодателя
    BTN_REVOKE_USER_CROSS = (By.XPATH, "//button[contains(@class, 'remove-user')]")
    BTN_CONFIRM_REVOKE = (By.XPATH, "//button[contains(., 'Закрыть доступ')]")
    TOAST_ERROR = (By.XPATH, "//div[contains(text(), \"Can't invite yourself\") or contains(@class, 'toast-error')]")

    @allure.step("Отправить приглашение на доступ к счету: '{email}'")
    def invite_user_to_account(self, email: str):
        self.driver.find_element(*self.TAB_ACCESS_SHARED).click()
        inp = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.EMAIL_SHARE_INPUT))
        inp.clear()
        inp.send_keys(email)
        self.driver.find_element(*self.BTN_ADD_EMAIL_PLUS).click()
        self.driver.find_element(*self.BTN_SAVE_SHARE).click()

    @allure.step("Принять приглашение к общему счету")
    def accept_shared_invitation(self):
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(self.MODAL_INVITE_CONTAINER))
        self.driver.find_element(*self.BTN_ACCEPT_INVITE).click()

    @allure.step("Отклонить приглашение к общему счету")
    def reject_shared_invitation(self):
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(self.MODAL_INVITE_CONTAINER))
        self.driver.find_element(*self.BTN_REJECT_INVITE).click()

    @allure.step("Отказаться от отслеживания счета")
    def untrack_account(self, confirm=True):
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(self.MODAL_UNTRACK_CONFIRM))
        if confirm:
            self.driver.find_element(*self.BTN_UNTRACK_CONFIRM).click()
        else:
            self.driver.find_element(*self.BTN_MODAL_CLOSE_CROSS).click()