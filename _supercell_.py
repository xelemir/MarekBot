import requests

headers_coc = {
    'Accept': 'application.json',
    'authorization': 'Bearer TODO_YOUR_CLASH_OF_CLANS_API_TOKEN'
}

def get_json(url):
    response = requests.get(url, headers=headers_coc)
    json = response.json()
    return json

def user(user_id):
    return get_json("https://api.clashofclans.com/v1/players/%23" + user_id)

def cw_info(clan_id):
    return get_json("https://api.clashofclans.com/v1/clans/%23" + clan_id + "/currentwar")

def clan_info(clan_id):
    return get_json("https://api.clashofclans.com/v1/clans/%23" + clan_id)

def clan_members(clan_id):
    return get_json("https://api.clashofclans.com/v1/clans/" + clan_id + "/members")
