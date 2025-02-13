from flask import Flask, Response, jsonify
from utils.stract_api_client import StractAPIClient
import csv
import io


app = Flask(__name__)
client = StractAPIClient()


def generate_csv_response(data: list):
    """
    Gera uma resposta de texto em formato CSV válido.

    A resposta é retornada com o cabeçalho 'Content-Type' definindo o contéudo como texto plano.
    Garantindo que o conteúdo CSV seja exibido como texto na página.
    """
    if not data or not isinstance(data, list):
        return Response("", content_type="text/plain")
    # Usando IO para trabalhar com o CSV em mémoria.
    # Tirando necessidade de criar um arquivo em mémoria física, que nesse caso não é necessário
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    csv_data = output.getvalue()
    output.close()
    # Alterar para "text/csv" para 
    return Response(csv_data, content_type="text/plain; charset=utf-8")


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
    ads_data = list()
    accounts = client.get_platform_accounts(platform)
    if not accounts:
        return Response("Platform not found", status=404, content_type="text/plain")
    platform_fields = client.get_platform_fields(platform)
    for account in accounts:
        account_insights = client.get_platform_account_insights(
            platform,
            account["id"],
            account["token"],
            fields=(field["value"] for field in platform_fields)
        )
        for insight in account_insights:
            insight_data = {
                "Platform": platform,
                "Account Name": account["name"]
            }
            for field in platform_fields:
                insight_data[field["text"]] = insight[field["value"]]
            ads_data.append(insight_data)
    return generate_csv_response(ads_data)


@app.route("/<platform>/resumo")
def platform_ads_summarize(platform):
    all_accounts_data = list()
    accounts = client.get_platform_accounts(platform)
    if not accounts:
        return Response("Platform not found", status=404, content_type="text/plain")
    platform_fields = client.get_platform_fields(platform)
    for account in accounts:
        account_ads_data = {
            "Platform": platform,
            "Account Name": account["name"],
            "Account ID": account["id"]
        }
        account_insights = client.get_platform_account_insights(
            platform,
            account["id"],
            account["token"],
            fields=(field["value"] for field in platform_fields)
        )
        for insight in account_insights:
            for field in platform_fields:
                insight_value = insight[field["value"]]
                if not isinstance(insight_value, (int, float)):
                    continue
                if field["text"] in account_ads_data:
                    account_ads_data[field["text"]] += insight_value
                else:
                    account_ads_data[field["text"]] = insight_value
        all_accounts_data.append(account_ads_data)
    return generate_csv_response(all_accounts_data)


@app.route("/geral")
def general_ads():
    all_platforms_data = list()
    platforms = client.get_platforms()
    for platform in platforms:
        platform_id = platform["value"]
        accounts = client.get_platform_accounts(platform_id)
        platform_fields = client.get_platform_fields(platform_id)
        for account in accounts:
            account_insights = client.get_platform_account_insights(
                platform_id,
                account["id"],
                account["token"],
                fields=(field["value"] for field in platform_fields)
            )
            for insight in account_insights:
                insight_data = {
                    "Platform": platform["text"],
                    "Account Name": account["name"]
                }
                for field in platform_fields:
                    insight_data[field["text"]] = insight.get(field["value"], None)
                all_platforms_data.append(insight_data)
    return generate_csv_response(all_platforms_data)


@app.route("/geral/resumo")
def general_platforms_ads_summarize():
    all_platforms_data = list()
    platforms = client.get_platforms()
    for platform in platforms:
        account_ads_data = {
            "Platform": platform["text"],
        }
        platform_id = platform["value"]
        accounts = client.get_platform_accounts(platform_id)
        platform_fields = client.get_platform_fields(platform_id)
        for account in accounts:
            account_insights = client.get_platform_account_insights(
                platform_id,
                account["id"],
                account["token"],
                fields=(field["value"] for field in platform_fields)
            )
            for insight in account_insights:
                for field in platform_fields:
                    insight_value = insight[field["value"]]
                    if not isinstance(insight_value, (int, float)):
                        continue
                    if field["text"] in account_ads_data:
                        account_ads_data[field["text"]] += insight_value
                    else:
                        account_ads_data[field["text"]] = insight_value
        all_platforms_data.append(account_ads_data)
    return generate_csv_response(all_platforms_data)
