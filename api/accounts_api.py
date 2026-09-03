import requests
import allure
from datetime import datetime, timezone

class AccountsAPI:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.frontend_url = self.base_url
        self.is_qa = "qa" in self.frontend_url

        # Централизованное определение базовых URL в зависимости от стенда
        if self.is_qa:
            self.wallet_api_url = "https://wallet-api.qa.profinansy.dev"
            self.core_api_url = "https://qa.profinansy.dev"
        else:
            self.wallet_api_url = "https://wallet-api.profinansy.ru"
            self.core_api_url = "https://profinansy.ru"

        self.token = token
        self.session = requests.Session()
        self.session.verify = False

    def _get_headers(self, accept_json: bool = True) -> dict:
        """Общие заголовки для всех запросов с опорой на текущий стенд"""
        return {
            "accept": "application/json, text/plain, */*" if accept_json else "*/*",
            "content-type": "application/json",
            "origin": self.frontend_url,
            "referer": f"{self.frontend_url}/",
            "token": self.token,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site"
        }

    @allure.step("API: Создать дебетовый счет '{title}'")
    def create_debit_account(
        self, 
        title: str, 
        initial_balance: float = 1000.0, 
        currency_id: int = 1, 
        color: str = "#FF0000"
    ) -> dict:
        """Создает дебетовый счет через API"""
        url = f"{self.wallet_api_url}/api/v3/expenses/bank_accounts/"

        payload = {
            "title": title,
            "icon_id": None,
            "icon_background_color": color,
            "background_id": None,
            "currency_id": currency_id,
            "initial_balance": initial_balance
        }

        response = self.session.post(url, json=payload, headers=self._get_headers())
        if response.status_code in [200, 201]:
            print(f"[API] Дебетовый счет '{title}' успешно создан!")
            return response.json()

        raise RuntimeError(f"[API ERROR] Не удалось создать дебетовый счет '{title}'! [{response.status_code}] {response.text}")

    @allure.step("API: Создать кредитную карту '{title}'")
    def create_credit_card_account(
        self, 
        title: str, 
        initial_balance: float = 1000.0, 
        limit_amount: float = 15000.0,
        currency_id: int = 1, 
        color: str = "#FF0000"
    ) -> dict:
        """Создает кредитную карту через API (account_type: 'C')"""
        url = f"{self.wallet_api_url}/api/v3/expenses/bank_accounts/"

        payload = {
            "title": title,
            "icon_background_color": color,
            "initial_balance": initial_balance,
            "account_type": "C",
            "currency_id": currency_id,
            "limit_amount": limit_amount,
            "show_credit_money": False
        }

        response = self.session.post(url, json=payload, headers=self._get_headers())
        if response.status_code in [200, 201]:
            print(f"[API] Кредитная карта '{title}' успешно создана!")
            return response.json()

        raise RuntimeError(f"[API ERROR] Не удалось создать кредитную карту '{title}'! [{response.status_code}] {response.text}")

    @allure.step("API: Создать накопительный счет '{title}'")
    def create_savings_account(
        self, 
        title: str, 
        initial_balance: float = 1000.0,
        currency_id: int = 1,
        color: str = ""
    ) -> dict:
        """Создает накопительный счет через API"""
        url = f"{self.wallet_api_url}/api/v3/accumulations/accumulations_accounts/"

        payload = {
            "title": title,
            "icon_background_color": color,
            "initial_balance": initial_balance,
            "currency_id": currency_id
        }

        response = self.session.post(url, json=payload, headers=self._get_headers())
        if response.status_code in [200, 201]:
            print(f"[API] Накопительный счет '{title}' успешно создан!")
            return response.json()

        raise RuntimeError(f"[API ERROR] Не удалось создать накопительный счет '{title}'! [{response.status_code}] {response.text}")

    @allure.step("API: Создать инвест-счет (портфель) '{title}'")
    def create_investment_account(
        self, 
        title: str, 
        init_transaction: float = 15000.0,
        currency: str = "RUB"
    ) -> dict:
        """Создает портфель через API в заданной валюте"""
        url = f"{self.core_api_url}/api/portfolios/addPortfolio"
        created_date = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")

        payload = {
            "title": title,
            "wallet": currency,  # Теперь валюта динамическая
            "is_public": False,
            "only_link": False,
            "created_date": created_date,
            "risk_profile": "careful",
            "short_description": "",
            "autoEvents": {
                "dividends": False,
                "coupons": False,
                "amortizations": True,
                "splits": True
            },
            "init_transaction": init_transaction,
            "use_capital": True,
            "is_idv": False,
            "show_in_budget": True
        }

        response = self.session.post(url, json=payload, headers=self._get_headers(accept_json=False))
        if response.status_code in [200, 201]:
            print(f"[API] Инвест-счет '{title}' ({currency}) успешно создан!")
            return response.json()

        raise RuntimeError(f"[API ERROR] Не удалось создать инвест-счет '{title}'! [{response.status_code}] {response.text}")

    @allure.step("API: Удалить счет с ID '{account_id}'")
    def delete_account(self, account_id: str):
        """Удаляет дебетовый/кредитный счет через API по его ID (UUID)"""
        if not account_id:
            print("[API WARNING] Передан пустой ID для удаления счета. Отмена.")
            return

        url = f"{self.wallet_api_url}/api/v3/expenses/bank_accounts/{account_id}/"

        try:
            response = self.session.delete(url, headers=self._get_headers())
            if response.status_code in [200, 204]:
                print(f"[API TEARDOWN] Счет {account_id} успешно удален!")
            else:
                print(f"[API TEARDOWN ERROR] Ошибка {response.status_code} при удалении: {response.text}")
        except Exception as e:
            print(f"[API TEARDOWN ERROR] Исключение при удалении счета {account_id}: {str(e)}")

    @allure.step("API: Удалить накопительный счет с ID '{account_id}'")
    def delete_accumulation_account(self, account_id: str):
        """Удаляет накопительный счет по ID"""
        if not account_id:
            return

        url = f"{self.wallet_api_url}/api/v3/accumulations/accumulations_accounts/{account_id}/"

        try:
            response = self.session.delete(url, headers=self._get_headers())
            if response.status_code in [200, 204]:
                print(f"[API TEARDOWN] Накопительный счет {account_id} успешно удален!")
            else:
                print(f"[API TEARDOWN ERROR] Ошибка {response.status_code} при удалении накопительного счета {account_id}: {response.text}")
        except Exception as e:
            print(f"[API TEARDOWN ERROR] Исключение при удалении накопительного счета {account_id}: {str(e)}")

    @allure.step("API: Удалить инвест-счет (портфель) с ID '{portfolio_id}'")
    def delete_investment_account(self, portfolio_id):
        """Удаляет инвест-портфель по ID"""
        if not portfolio_id:
            return

        url = f"{self.core_api_url}/api/portfolios/portfolio/{portfolio_id}?is_archive=false"

        try:
            response = self.session.delete(url, headers=self._get_headers(accept_json=False))
            if response.status_code in [200, 204]:
                print(f"[API TEARDOWN] Инвест-счет {portfolio_id} успешно удален!")
            else:
                print(f"[API TEARDOWN ERROR] Ошибка {response.status_code} при удалении инвест-счета {portfolio_id}: {response.text}")
        except Exception as e:
            print(f"[API TEARDOWN ERROR] Исключение при удалении инвест-счета {portfolio_id}: {str(e)}")