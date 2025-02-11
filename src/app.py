from flask import Flask, Response, jsonify
from utils.stract_api_client import StractAPIClient
from typing import Literal
import pandas as pd


app = Flask(__name__)
client = StractAPIClient()


def get_platform_accounts(platform_id) -> list[dict]:
    platform_accounts_res = client.get_platform_accounts(platform_id)
    if "error" in platform_accounts_res:
        return []
    platform_accounts: list = platform_accounts_res["accounts"]
    if "pagination" in platform_accounts_res:
        total_pages = platform_accounts_res["pagination"]["total"]
        for page_index in range(2, (total_pages + 1)):
            indexed_response = client.get_platform_accounts(platform_id, page_index)
            platform_accounts.extend(indexed_response["accounts"])
    return platform_accounts


def get_platform_fields(platform_id) -> list[dict]:
    platform_fields_res = client.get_platform_fields(platform_id)
    platform_fields: list = platform_fields_res["fields"]
    if "pagination" in platform_fields_res:
        total_pages = platform_fields_res["pagination"]["total"]
        for page in range(2, (total_pages + 1)):
            # Adding
            indexed_response = client.get_platform_fields(platform_id, page)
            platform_fields.extend(indexed_response["fields"])
    return platform_fields


def generate_csv_response(data: list, filename="data.csv"):
    if not data or not isinstance(data, list):
        return Response("", content_type="text/plain")
    headers = data[0].keys()
    csv_data = ",".join(headers) + "\n"
    csv_data += "\n".join([",".join(str(row.get(h)) for h in headers) for row in data])
    # Return
    response = Response(csv_data, content_type="text/plain")
    return response


def get_platform_ads_data(platform_id) -> list[dict]:
    ads_data = list()
    accounts = get_platform_accounts(platform_id)
    if not accounts:
        return Response("Platform not found", status=404, content_type="text/plain")
    platform_fields = get_platform_fields(platform_id)
    fields_id_name_map = {field["value"]: field["text"] for field in platform_fields}
    for account in accounts:
        account_insights = client.get_platform_account_insights(
            platform_id,
            account["id"],
            account["token"],
            fields=list(fields_id_name_map.keys())
        )
        for insight in account_insights["insights"]:
            insight_data = {
                "Platform": platform_id,
                "Account Name": account["name"]
            }
            for field_id in fields_id_name_map:
                field_name = fields_id_name_map[field_id]
                insight_data[field_name] = insight[field_id]
            ads_data.append(insight_data)
    return ads_data


@app.route("/")
def home():
    return jsonify({
        "name": "Davi Rodrigues Chiqueti",
        "email": "davichiqueti@gmail.com",
        "linkedin": "www.linkedin.com/in/davi-chiqueti-5a956a247"
    })


@app.route("/<platform>/")
def platform_ads(platform):
    ads_data = get_platform_ads_data(platform)
    return generate_csv_response(ads_data)


@app.route("/<platform>/resumo")
def platform_ads_summarize(platform):
    all_accounts_data = list()
    accounts = get_platform_accounts(platform)
    if not accounts:
        return Response("Platform not found", status=404, content_type="text/plain")
    platform_fields = get_platform_fields(platform)
    fields_id_name_map = {field["value"]: field["text"] for field in platform_fields}
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
            fields=list(fields_id_name_map.keys())
        )
        for insight in account_insights["insights"]:
            for field_id in fields_id_name_map:
                field_value = insight[field_id]
                if isinstance(field_value, (int, float)):
                    field_name = fields_id_name_map[field_id]
                    if field_name in account_ads_data:
                        account_ads_data[field_name] += insight[field_id]
                    else:
                        account_ads_data[field_name] = insight[field_id]
        all_accounts_data.append(account_ads_data)
    return generate_csv_response(all_accounts_data)


@app.route("/geral")
def general_ads():
    all_platforms_data = list()
    platforms = client.get_platforms()["platforms"]
    for platform in platforms:
        platform_id = platform["value"]
        accounts = get_platform_accounts(platform_id)
        platform_fields = get_platform_fields(platform_id)
        fields_id_name_map = {field["value"]: field["text"] for field in platform_fields}
        for account in accounts:
            account_insights = client.get_platform_account_insights(
                platform_id,
                account["id"],
                account["token"],
                fields=list(fields_id_name_map.keys())
            )
            for insight in account_insights["insights"]:
                insight_data = {
                    "Platform": platform["text"],
                    "Account Name": account["name"]
                }
                for field_id in fields_id_name_map:
                    field_name = fields_id_name_map[field_id]
                    insight_data[field_name] = insight.get(field_id, None)
                all_platforms_data.append(insight_data)
    return generate_csv_response(all_platforms_data)


@app.route("/geral/resumo")
def general_platforms_ads_summarize():
    all_platforms_data = list()
    platforms = client.get_platforms()["platforms"]
    for platform in platforms:
        account_ads_data = {
            "Platform": platform["text"],
        }
        platform_id = platform["value"]
        accounts = get_platform_accounts(platform_id)
        platform_fields = get_platform_fields(platform_id)
        fields_id_name_map = {field["value"]: field["text"] for field in platform_fields}
        for account in accounts:
            account_insights = client.get_platform_account_insights(
                platform_id,
                account["id"],
                account["token"],
                fields=list(fields_id_name_map.keys())
            )
            for insight in account_insights["insights"]:
                for field_id in fields_id_name_map:
                    field_value = insight[field_id]
                    if isinstance(field_value, (int, float)):
                        field_name = fields_id_name_map[field_id]
                        if field_name in account_ads_data:
                            account_ads_data[field_name] += insight[field_id]
                        else:
                            account_ads_data[field_name] = insight[field_id]
        all_platforms_data.append(account_ads_data)
    return generate_csv_response(all_platforms_data)
