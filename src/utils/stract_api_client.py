import requests


class StractAPIClient:
    """
    A class to interact with the Stract API. Providing easy methods to acess resources.
    """

    BASE_API_URL = "https://sidebar.stract.to/api"
    __API_AUTH_HEADERS = {
        "Authorization": "Bearer ProcessoSeletivoStract2025"
    }

    def request(self, path: str, method: str = "get", **kwargs):
        """
        Generic Auxiliar Private Method to send requests
        """
        uri = self.BASE_API_URL + path
        return requests.request(method, uri, headers=self.__API_AUTH_HEADERS, **kwargs).json()

    def get_platforms(self):
        return self.request("/platforms")

    def get_platform_fields(self, platform_id: str, page: int = 1):
        return self.request(f"/fields?platform={platform_id}&page={page}")

    def get_platform_accounts(self, platform_id: str, page: int = 1, auto_pagination: bool = True):
        return self.request(f"/accounts?platform={platform_id}&page={page}")
        if auto_pagination:
            first_page_response = self.request(
                f"/accounts?platform={platform_id}&page=1")
            accounts: list = first_page_response["accounts"]
            if "pagination" not in first_page_response:
                return accounts
            total_pages = first_page_response["pagination"]["total"]
            for page_index in range(2, (total_pages + 1)):
                index_page_response = self.request(
                    f"/accounts?platform={platform_id}&page={page_index}")
                accounts.extend(index_page_response["accounts"])
            return accounts
        else:
            return self.request(f"/accounts?platform={platform_id}&page={page}")["accounts"]

    def get_platform_account_insights(self, platform_id: str, account_id: str, user_token: str, fields: list[str]):
        return self.request(
            path="/insights",
            params={
                "platform": platform_id,
                "account": account_id,
                "token": user_token,
                "fields": ','.join(fields)
            }
        )
