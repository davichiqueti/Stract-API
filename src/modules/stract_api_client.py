import requests


class StractAPIClient:
    """
    Classe para interagir com a API da Stract.
    
    Agindo como um Client que prove metódos que facilitam o acesso a recursos.

    Além de isolar as requisições a essa API em uma única abstração.
    """

    BASE_API_URL = "https://sidebar.stract.to/api"
    __API_AUTH_HEADERS = {
        # Mantendo token hard-coded para facilitar a avaliação do desafio.
        # Em um projeto real, eu leria esse token de uma váriavel de ambiente. A URL também, caso ela fosse sigilosa
        "Authorization": "Bearer ProcessoSeletivoStract2025"
    }

    def __request(self, path: str, method: str = "get", **kwargs):
        """
        Método privado para fazer as requisições usando configurações base.

        Args:
            path: o caminho do recurso a ser acessado sem a URL base da api.
            method: o método HTTP que deve ser executad.
        Raises:
            HTTPError: Se algum erro identificado pelo status code da resposta for gerado.
        """
        uri = self.BASE_API_URL + path
        response = requests.request(method, uri, headers=self.__API_AUTH_HEADERS, **kwargs)
        response.raise_for_status()
        return response.json()

    def get_platforms(self):
        return self.__request("/platforms")["platforms"]

    def get_platform_account_insights(
        self,
        platform_id: str,
        account_id: str,
        user_token: str,
        fields: list[str]
    ) -> list[dict]:
        res = self.__request(
            path="/insights",
            params={
                "platform": platform_id,
                "account": account_id,
                "token": user_token,
                "fields": ','.join(fields)
            }
        )
        return res["insights"]

    def get_platform_fields(self, platform_id: str) -> list[dict]:
        platform_fields_res = self.__request(f"/fields?platform={platform_id}&page=1")
        if "error" in platform_fields_res:
            return []
        platform_fields: list[dict] = platform_fields_res["fields"]
        if "pagination" in platform_fields_res:
            total_pages = platform_fields_res["pagination"]["total"]
            for page_index in range(2, (total_pages + 1)):
                indexed_response = self.__request(f"/fields?platform={platform_id}&page={page_index}")
                platform_fields.extend(indexed_response["fields"])
        return platform_fields

    def get_platform_accounts(self, platform_id: str) -> list[dict]:
        platform_accounts_res = self.__request(f"/accounts?platform={platform_id}&page=1")
        if "error" in platform_accounts_res:
            return []
        platform_accounts: list[dict] = platform_accounts_res["accounts"]
        if "pagination" in platform_accounts_res:
            total_pages = platform_accounts_res["pagination"]["total"]
            for page_index in range(2, (total_pages + 1)):
                indexed_response = self.__request(f"/accounts?platform={platform_id}&page={page_index}")
                platform_accounts.extend(indexed_response["accounts"])
        return platform_accounts
