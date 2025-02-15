from flask import Flask, Response, jsonify, abort
from modules.stract_api_client import StractAPIClient
import pandas as pd


app = Flask(__name__)
client = StractAPIClient()


def generate_csv_response(data: pd.DataFrame):
    """
    Recebe um Dataframe e o resposta em uma resposta no formato CSV.

    Função feita para unificar o processamento da resposta.
    """
    # Substituindo colunas com representação vazia do pandas por uma string vazia
    data.fillna('')
    return Response(
        data.to_csv(index=False),
        # Definindo o countéudo como texto para que o CSV seja apresentado no navegador
        # Ao invés de "text/csv" que faria com que o arquivo fosse baixado em navegadores padrão
        content_type="text/plain; charset=utf-8"
    )


def get_platform_insights(platform_id: str, platform_name: str) -> pd.DataFrame:
    """
    Acessa todos os recursos com a ordem necessária para extrair todos os insights de uma plataforma
    
    Retornando os insights como um Dataframe Pandas
    """
    # Getting accounts
    accounts = client.get_platform_accounts(platform_id)
    platform_fields = client.get_platform_fields(platform_id)
    all_insights = []
    # Processing insights
    for account in accounts:
        account_insights = client.get_platform_account_insights(
            platform_id=platform_id,
            account_id=account["id"],
            user_token=account["token"],
            fields=(field["value"] for field in platform_fields)
        )
        for insight in account_insights:
            insight_data = {
                "Platform": platform_name,
                "Account": account["name"],
                "Account ID": account["id"]
            }
            for field in platform_fields:
                insight_data[field["text"]] = insight.get(field["value"], None)
            if platform_id == "ga4":
                # Gerando a coluna de custo por click para o google ads
                insight_data["Cost Per Click"] = round((insight_data["Spend"] / insight_data["Clicks"]), 2)
            all_insights.append(insight_data)
    # Returning result as Pandas dataframe
    return pd.DataFrame(all_insights)


def validate_platform(platform) -> dict:
    """
    Checa se uma plataforma é válida e carrega suas informações caso encontrada.

    Utilizada em requisições com parametro de plataforma. Permite a checagem por nome ou ID.
    Aborta a requisição retornando uma resposta com status 404 caso a plataforma não seja encontrada
    """
    plataforms = client.get_platforms()
    for existent_platform in plataforms:
        platform_id = existent_platform["value"]
        platform_name = existent_platform["text"]
        if platform in [platform_id, platform_name]:
            return {
                "id": platform_id,
                "name": platform_name
            }
    # Abortando a operação e retornando um código de erro para plataforma não encontrada
    abort(code=404, description="Platform not found")


@app.route("/")
def home():
    return jsonify({
        "name": "Davi Rodrigues Chiqueti",
        "email": "davichiqueti@gmail.com",
        "linkedin": "www.linkedin.com/in/davi-chiqueti-5a956a247"
    })


@app.route("/<platform>/", strict_slashes=False)
def platform_ads(platform):
    if platform == "geral":
        return general_ads()
    plataform_info = validate_platform(platform)
    insights = get_platform_insights(plataform_info["id"], plataform_info["name"])
    return generate_csv_response(insights)


@app.route("/<platform>/resumo")
def platform_ads_summarize(platform):
    # Checagem se a plataforma existe. Também auxilia a encontrar o nome para busca por ID e vice e versa
    # Permitindo ambos os tipos como um parametro válido
    plataform_info = validate_platform(platform)
    insights = get_platform_insights(plataform_info["id"], plataform_info["name"])
    # Agrupando insights por ID da conta. Já que o nome da conta não é único
    grouped_insights = insights.groupby("Account ID").sum(numeric_only=True).reset_index()
    grouped_insights.insert(0, "Platform", insights["Platform"])
    grouped_insights.insert(1, "Account", insights["Account"])
    for col in insights.select_dtypes(include=['object']).columns:
        if col not in grouped_insights.columns:
            grouped_insights[col] = None
    return generate_csv_response(grouped_insights)


@app.route("/geral")
def general_ads():
    platforms = client.get_platforms()
    insights = pd.DataFrame()
    for platform in platforms:
        platform_id = platform["value"]
        platform_name = platform["text"]
        platform_insights = get_platform_insights(platform_id, platform_name)
        insights = pd.concat([insights, platform_insights], axis=0)
    return generate_csv_response(insights)


@app.route("/geral/resumo")
def general_platforms_ads_summarize():
    platforms = client.get_platforms()
    insights = pd.DataFrame()
    for platform in platforms:
        platform_id = platform["value"]
        platform_name = platform["text"]
        platform_insights = get_platform_insights(platform_id, platform_name)
        insights = pd.concat([insights, platform_insights], axis=0)
    # Agrupando por plataforma
    grouped_insights = insights.groupby("Platform")
    # Somando os valores e tirando o índice de plataforma criado no agrupamento.
    # Usando "min_count", quando uma plataforma não tem uma coluna númerica, seu valor é nulo ao inves de 0.
    grouped_insights = grouped_insights.sum(numeric_only=True, min_count=1).reset_index()
    # Garantindo que colunas de texto estejam presentes, porém com valor nulo
    for col in insights.select_dtypes(include=['object']).columns:
        if col not in grouped_insights.columns:
            grouped_insights[col] = None
    return generate_csv_response(grouped_insights)
