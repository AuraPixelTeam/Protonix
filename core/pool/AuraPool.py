import requests
import json


def register_pool(server_hash, worker_name, hash_id, app_name, data):
    url = "https://dash.aurateam.org/query/api.php"

    payload = {
        "event": "register",
        "server_hash": server_hash,
        "worker_name": worker_name,
        "hash_id": hash_id,
        "app_name": app_name,
        "data": json.dumps(data)
    }
    headers = {"Content-Type": "application/json"}

    response = requests.request("POST", url, json=payload, headers=headers)

    return response.json()


def update_pool(server_hash, hash_id, data):
    url = "https://dash.aurateam.org/query/api.php"

    payload = {
        "event": "update",
        "server_hash": server_hash,
        "hash_id": hash_id,
        "data": json.dumps(data)
    }
    headers = {"Content-Type": "application/json"}

    response = requests.request("POST", url, json=payload, headers=headers)

    return response.json()
