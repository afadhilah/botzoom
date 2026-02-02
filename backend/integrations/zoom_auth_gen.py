# import requests
# import base64

# ACCOUNT_ID = "MqAYOn13SzSucVAJd8tlFw"
# CLIENT_ID = "Sq6nnOz7SMyOfLcn0_b3w"
# CLIENT_SECRET = "WP5r4H8F98nxs39oGM6tmGBQg2DVI1fz"

# def get_zoom_token():
#     creds = f"{CLIENT_ID}:{CLIENT_SECRET}"
#     b64 = base64.b64encode(creds.encode()).decode()

#     url = "https://zoom.us/oauth/token"
#     params = {
#         "grant_type": "account_credentials",
#         "account_id": ACCOUNT_ID
#     }

#     headers = {
#         "Authorization": f"Basic {b64}"
#     }

#     r = requests.post(url, params=params, headers=headers)
#     r.raise_for_status()
#     return r.json()["access_token"]

# token = get_zoom_token()
# print(token)
