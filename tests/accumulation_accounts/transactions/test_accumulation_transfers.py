import time
import allure
import pytest
from pages.dashboard_pages.dashboard_page import DashboardPage
from pages.debit_pages.accounts_main_page import AccountsMainPage
from pages.transactions_pages.transactions_modal_page import TransactionsModalPage


@allure.feature("Бюджет и Накопления")
@allure.story("Переводы и накопления")
class TestAccumulationTransfers:

    @allure.title("1. Наличие вкладки 'Накопления' и проверка состава формы создания")
    def test_accumulation_tab_presence_in_modal(self, api_logged_in_driver, accounts_api, api_account_cleanup_registry):
        driver = api_logged_in_driver
        dashboard_page = DashboardPage(driver)
        transaction_modal = TransactionsModalPage(driver)
        accounts_page = AccountsMainPage(driver)

        # 1. Быстрый запрос к API для создания дебетового счета
        debit_name = f"Дебет-{int(time.monotonic())}"
        create_response = accounts_api.create_debit_account(title=debit_name, initial_balance=1000)
        
        # 2. Извлекаем ID счета из ответа и добавляем в реестр на удаление
        account_id = create_response.get("id") or create_response.get("data", {}).get("id")
        if account_id:
            api_account_cleanup_registry.append(account_id)
        else:
            print(f"[WARNING] Не удалось извлечь ID счета из ответа: {create_response}")

        # 3. Обновляем интерфейс для синхронизации
        driver.refresh()

        #закрытие модалки для выбора режима бюджета
        accounts_page.close_budget_interface_modal_if_present()

        # 4. Переходим к добавлению операции
        dashboard_page.open_add_transaction_modal()
        
        # Шаг 1: Проверяем наличие вкладки
        assert transaction_modal.is_accumulation_tab_visible(), "Вкладка 'Накопления' не отображается в модальном окне!"
        
        # Шаг 2: Переходим на вкладку "Накопления"
        transaction_modal.open_accumulation_tab()
        
        # Шаг 3: Проверяем наличие всех полей
        assert transaction_modal.check_accumulation_form_fields_present(), "Не все поля отображаются на форме!"
        
        # Шаг 4: Проверяем индикацию обязательных полей (звездочки)
        assert transaction_modal.check_mandatory_fields_asterisks(), "Не все обязательные поля отмечены звездочкой!"
        

    @allure.title("2. Выбор любого счета (дебетового, накопительного, инвест, кредитного) в поле 'Счет списания' после клика на Все счета")
    def test_source_account_dropdown_allows_any_account(self, api_logged_in_driver, accounts_api, api_account_cleanup_registry):
        driver = api_logged_in_driver
        dashboard_page = DashboardPage(driver)
        transaction_modal = TransactionsModalPage(driver)
        accounts_page = AccountsMainPage(driver)

        timestamp = int(time.monotonic())
        debit_name = f"Дебет-{timestamp}"
        savings_name = f"Накоп-{timestamp}"
        credit_name = f"Кредитка-{timestamp}"
        invest_name = f"Инвест-{timestamp}"

        # 1. Дебетовый счет -> СРАЗУ в реестр
        debit_res = accounts_api.create_debit_account(title=debit_name, initial_balance=1000)
        if debit_id := (debit_res.get("id") or debit_res.get("data", {}).get("id")):
            api_account_cleanup_registry.append(("bank", debit_id))

        # 2. Накопительный счет -> СРАЗУ в реестр
        savings_res = accounts_api.create_savings_account(title=savings_name, initial_balance=1000)
        if savings_id := (savings_res.get("id") or savings_res.get("data", {}).get("id")):
            api_account_cleanup_registry.append(("accumulation", savings_id))

        # 3. Кредитная карта -> СРАЗУ в реестр
        credit_res = accounts_api.create_credit_card_account(title=credit_name, initial_balance=1000, limit_amount=15000)
        if credit_id := (credit_res.get("id") or credit_res.get("data", {}).get("id")):
            api_account_cleanup_registry.append(("bank", credit_id))

        # 4. Инвест-счет -> СРАЗУ в реестр
        invest_res = accounts_api.create_investment_account(title=invest_name, init_transaction=15000)
        if invest_id := (invest_res.get("id") or invest_res.get("data", {}).get("id")):
            api_account_cleanup_registry.append(("investment", invest_id))

        # 5. Синхронизируем UI
        driver.get(f"{driver.base_url.rstrip('/')}/wallet/accounts")
        time.sleep(3)

        #закрытие модалки для выбора режима бюджета
        accounts_page.close_budget_interface_modal_if_present()

        # 6. Переход в модальное окно и открытие списка
        dashboard_page.click_all_accounts_card("Дебетовые")
        dashboard_page.open_add_transaction_modal()
        transaction_modal.open_accumulation_tab()
        transaction_modal.open_source_account_dropdown()

        # 7. Проверки отображения каждого счета
        assert transaction_modal.is_account_in_source_dropdown(debit_name), f"Дебетовый счет '{debit_name}' не найден в списании!"
        assert transaction_modal.is_account_in_source_dropdown(savings_name), f"Накопительный счет '{savings_name}' не найден в списании!"
        assert transaction_modal.is_account_in_source_dropdown(invest_name), f"Инвест-счет '{invest_name}' не найден в списании!"
        assert transaction_modal.is_account_in_source_dropdown(credit_name), f"Кредитная карта '{credit_name}' не найдена в списании!"

    @allure.title("3. Сложная фильтрация счетов в поле 'Куда' на вкладке Накопления")
    def test_accumulation_destination_filtering(self, api_logged_in_driver, accounts_api, api_account_cleanup_registry):
        driver = api_logged_in_driver
        dashboard_page = DashboardPage(driver)
        transaction_modal = TransactionsModalPage(driver)

        ts = int(time.monotonic())

        # Названия 12 счетов
        d_r1, d_r2, d_u = f"ДебРУБ1-{ts}", f"ДебРУБ2-{ts}", f"ДебUSD-{ts}"
        s_r1, s_r2, s_u = f"НакРУБ1-{ts}", f"НакРУБ2-{ts}", f"НакUSD-{ts}"
        c_r1, c_r2, c_u = f"КредРУБ1-{ts}", f"КредРУБ2-{ts}", f"КредUSD-{ts}"
        i_r1, i_r2, i_u = f"ИнвРУБ1-{ts}", f"ИнвРУБ2-{ts}", f"ИнвUSD-{ts}"

        # Компактные хелперы для создания счетов и мгновенной регистрации их на удаление
        def make_deb(name, curr=1):
            res = accounts_api.create_debit_account(title=name, currency_id=curr)
            if acc_id := (res.get("id") or res.get("data", {}).get("id")):
                api_account_cleanup_registry.append(("bank", acc_id))

        def make_sav(name, curr=1):
            res = accounts_api.create_savings_account(title=name, currency_id=curr)
            if acc_id := (res.get("id") or res.get("data", {}).get("id")):
                api_account_cleanup_registry.append(("accumulation", acc_id))

        def make_cred(name, curr=1):
            res = accounts_api.create_credit_card_account(title=name, currency_id=curr)
            if acc_id := (res.get("id") or res.get("data", {}).get("id")):
                api_account_cleanup_registry.append(("bank", acc_id))

        def make_inv(name, curr="RUB"):
            res = accounts_api.create_investment_account(title=name, currency=curr)
            if acc_id := (res.get("id") or res.get("data", {}).get("id")):
                api_account_cleanup_registry.append(("investment", acc_id))

        # 1. Создаем 12 счетов через API (1 - Рубли, 2 - Доллары)
        make_deb(d_r1); make_deb(d_r2); make_deb(d_u, curr=2)
        make_sav(s_r1); make_sav(s_r2); make_sav(s_u, curr=2)
        make_cred(c_r1); make_cred(c_r2); make_cred(c_u, curr=2)
        make_inv(i_r1); make_inv(i_r2); make_inv(i_u, curr="USD")

        # 2. Один чистый переход на главную страницу и открытие модалки
        driver.get(f"{driver.base_url.rstrip('/')}/wallet/accounts")
        time.sleep(4)
        
        # Надежно обновляем страницу, чтобы UI гарантированно подтянул 12 новых счетов с бэкенда
        driver.refresh()
        time.sleep(4)

        #закрываем модалки, сели такие есть
        accounts_page = AccountsMainPage(driver)
        try:
            accounts_page.close_promo_popup_if_present()
        except Exception:
            pass # Игнорируем, если метода нет или онбординг не появился
        #закрытие модалки для выбора режима бюджета
        accounts_page.close_budget_interface_modal_if_present()


        dashboard_page.click_all_accounts_card("Дебетовые")
        dashboard_page.open_add_transaction_modal()
        transaction_modal.open_accumulation_tab()

        # Хелпер для массовой проверки вариантов в выпадающем списке
        def verify_destinations(expected_in, expected_out):
            for acc in expected_in:
                assert transaction_modal.is_account_in_destination_dropdown(acc), f"Счет '{acc}' должен быть доступен!"
            for acc in expected_out:
                assert not transaction_modal.is_account_in_destination_dropdown(acc), f"Счет '{acc}' НЕ должен быть доступен!"

        # === ПРОВЕРКА 1: Выбран дебетовый счет в рублях (d_r1) ===
        transaction_modal.select_source_account(d_r1)
        verify_destinations(
            expected_in=[s_r1, s_r2, i_r1, i_r2],
            expected_out=[d_r1, d_r2, d_u, c_r1, c_r2, c_u, s_u, i_u]
        )

        # === ПРОВЕРКА 2: Выбран накопительный счет в рублях (s_r1) ===
        transaction_modal.select_source_account(s_r1)
        verify_destinations(
            expected_in=[d_r1, d_r2, s_r2, c_r1, c_r2, i_r1, i_r2],
            expected_out=[s_r1, s_u, d_u, c_u, i_u]
        )

        # === ПРОВЕРКА 3: Выбрана кредитная карта в рублях (c_r1) ===
        transaction_modal.select_source_account(c_r1)
        verify_destinations(
            expected_in=[s_r1, s_r2, i_r1, i_r2],
            expected_out=[c_r1, c_r2, c_u, d_r1, d_r2, d_u, s_u, i_u]
        )

        # === ПРОВЕРКА 4: Выбран инвест-счет в рублях (i_r1) ===
        transaction_modal.select_source_account(i_r1)
        verify_destinations(
            expected_in=[d_r1, d_r2, c_r1, c_r2],
            expected_out=[i_r1, i_r2, i_u, s_r1, s_r2, s_u, d_u, c_u]
        )

    @allure.title("4. Динамическое обновление сумм на карточках счетов без перезагрузки страницы после создания транзакции накопления")
    def test_card_balances_update_realtime_after_accumulation(self, api_logged_in_driver, accounts_api, api_account_cleanup_registry):
        driver = api_logged_in_driver
        accounts_page = AccountsMainPage(driver)
        transaction_modal = TransactionsModalPage(driver)

        ts = int(time.monotonic())
        debit_name = f"Дебет-{ts}"
        savings_name = f"Накоп-{ts}"

        # 1. Создаем счета с начальным балансом 1000 через API
        res_deb = accounts_api.create_debit_account(title=debit_name, initial_balance=1000)
        res_sav = accounts_api.create_savings_account(title=savings_name, initial_balance=1000)

        if deb_id := (res_deb.get("id") or res_deb.get("data", {}).get("id")):
            api_account_cleanup_registry.append(("bank", deb_id))
        if sav_id := (res_sav.get("id") or res_sav.get("data", {}).get("id")):
            api_account_cleanup_registry.append(("accumulation", sav_id))

        # 2. Переходим на страницу кошелька
        driver.get(f"{driver.base_url.rstrip('/')}/wallet/accounts")
        time.sleep(3)
        driver.refresh()
        time.sleep(3)

        try:
            accounts_page.close_promo_popup_if_present()
        except Exception:
            pass

        # 3. Переводим 100 рублей в накопления
        transaction_modal.create_accumulation_transaction(
            source=debit_name,
            destination=savings_name,
            amount="100"
        )

        # 4. Переключаемся на "Дебетовые и кредитки" и проверяем баланс
        accounts_page.switch_to_tab("Дебетовые и кредитки")
        deb_balance = accounts_page.get_account_card_balance(debit_name)
        assert deb_balance == "900,00 ₽", f"Баланс дебетового счета не обновился! Получено: '{deb_balance}'"

        # 5. Переключаемся на "Накопительные" и проверяем баланс
        accounts_page.switch_to_tab("Накопительные")
        sav_balance = accounts_page.get_account_card_balance(savings_name)
        assert sav_balance == "1 100,00 ₽", f"Баланс накопительного счета не обновился! Получено: '{sav_balance}'"


    @allure.title("5. Проверка корректности баланса 'Всего денег' без перезагрузки страницы после создания транзакции накопления")
    def test_total_money_balance_updates_without_page_reload(self, api_logged_in_driver, accounts_api, api_account_cleanup_registry):
        driver = api_logged_in_driver
        accounts_page = AccountsMainPage(driver)
        transaction_modal = TransactionsModalPage(driver)

        ts = int(time.monotonic())
        debit_name = f"Дебет-{ts}"
        savings_name = f"Накоп-{ts}"

        # 1. Создаем дебетовый и накопительный счета через API
        res_deb = accounts_api.create_debit_account(title=debit_name, initial_balance=1000)
        res_sav = accounts_api.create_savings_account(title=savings_name, initial_balance=1000)

        if deb_id := (res_deb.get("id") or res_deb.get("data", {}).get("id")):
            api_account_cleanup_registry.append(("bank", deb_id))
        if sav_id := (res_sav.get("id") or res_sav.get("data", {}).get("id")):
            api_account_cleanup_registry.append(("accumulation", sav_id))

        # 2. Переходим на страницу кошелька и обновляем UI
        driver.get(f"{driver.base_url.rstrip('/')}/wallet/accounts")
        time.sleep(3)
        driver.refresh()
        time.sleep(3)

        try:
            accounts_page.close_promo_popup_if_present()
        except Exception:
            pass

        # 3. Фиксируем начальный общий баланс "Всего денег"
        initial_total = accounts_page.get_total_money_balance()

        # 4. Переводим 100,25 с НАКОПИТЕЛЬНОГО счета на ДЕБЕТОВЫЙ
        transaction_modal.create_accumulation_transaction(
            source=savings_name,
            destination=debit_name,
            amount="100,25"
        )

        # 5. Проверяем, что общий баланс "Всего денег" не изменился после внутреннего перевода
        current_total = accounts_page.get_total_money_balance()
        assert current_total == initial_total, (
            f"Общий баланс изменился при внутреннем переводе! "
            f"Было: '{initial_total}', Стало: '{current_total}'"
        )

    #дописать, как транзакция отображается в истории при выборе карточки все счета, дебетового счета, все накопительные и накопительного    

    @allure.title("6. Удаление дебетового счета: отмена транзакции, возврат баланса и очистка аналитики")
    def test_debit_account_deletion_resets_savings_and_clears_history(self, api_logged_in_driver, account_cleanup_registry):
        accounts_page = AccountsMainPage(api_logged_in_driver)
        transaction_modal = TransactionsModalPage(api_logged_in_driver)

        debit_name = f"Дебет-{int(time.monotonic())}"
        savings_name = f"Накоп-{int(time.monotonic())}"
        
        # Регистрируем счета в реестре UI-очистки на случай падения теста
        account_cleanup_registry.append(debit_name)
        account_cleanup_registry.append(savings_name)

        accounts_page.create_debit_account(debit_name, balance="1000")
        accounts_page.create_savings_account(savings_name, balance="1000")
        
        transaction_modal.create_accumulation_transaction(source=debit_name, destination=savings_name, amount="100")
        
        # Основной шаг: удаляем дебетовый счет
        accounts_page.delete_account_by_name(debit_name)
        
        # Проверки
        assert accounts_page.get_account_card_balance(savings_name) == "1 000,00 ₽", "Баланс накопительного счета не вернулся к исходному!"
        assert accounts_page.get_analytics_accumulation_value() == "0 ₽", "В аналитике значение накоплений не стало 0!"
        assert not accounts_page.is_transaction_in_history(debit_name), "Транзакция все еще отображается в истории!"

        # Удаление оставшегося накопительного счета после завершения проверок
        accounts_page.delete_account_by_name(savings_name)

    @allure.title("7. Удаление накопительного счета: отмена транзакции, возврат дебетового баланса и очистка аналитики")
    def test_savings_account_deletion_resets_debit_and_clears_history(self, api_logged_in_driver, account_cleanup_registry):
        accounts_page = AccountsMainPage(api_logged_in_driver)
        transaction_modal = TransactionsModalPage(api_logged_in_driver)

        debit_name = f"Дебет-{int(time.monotonic())}"
        savings_name = f"Накоп-{int(time.monotonic())}"

        # Регистрируем счета в реестре UI-очистки на случай падения теста
        account_cleanup_registry.append(debit_name)
        account_cleanup_registry.append(savings_name)

        accounts_page.create_debit_account(debit_name, balance="1000")
        accounts_page.create_savings_account(savings_name, balance="1000")
        
        transaction_modal.create_accumulation_transaction(source=debit_name, destination=savings_name, amount="100")
        
        # Основной шаг: удаляем накопительный счет
        accounts_page.delete_account_by_name(savings_name)
        
        # Проверки
        assert accounts_page.get_account_card_balance(debit_name) == "1 000,00 ₽", "Баланс дебетового счета не вернулся к исходному!"
        assert accounts_page.get_analytics_accumulation_value() == "0 ₽", "В аналитике значение накоплений не стало 0!"
        assert not accounts_page.is_transaction_in_history(savings_name), "Транзакция все еще отображается в истории!"

        # Удаление оставшегося дебетового счета после завершения проверок
        accounts_page.delete_account_by_name(debit_name)