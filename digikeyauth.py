import re
import requests
import cgi
import cgitb
import os
import ssl
import sys
import json
import datetime
import uuid
import logging
from requests.api import get


def Digikeyauth(event, context):
    try:
        postdata = json.loads(event['body'])
        code = postdata['code']
        accessdata = {
            "code": code,
            "client_id": "LttNhtAWuhAxykn3fDdkrvOaAWgDUXro",
            "client_secret": "CHRfGUIhMBqYDiIJ",
            "redirect_uri": "https://www.momenttrack.com/DigiKey",
            "grant_type": "authorization_code"
        }
        getaccesstoken = requests.post(
            "https://api.digikey.com/v1/oauth2/token", data=accessdata)
        getaccesstokendir = json.dumps(getaccesstoken.json())
        getaccesstokenloads = json.loads(getaccesstokendir)
        logging.info(getaccesstokenloads)
        logging.info(code)
        if 'access_token' in getaccesstokenloads:
            accesstoken = getaccesstokenloads['access_token']
            datareturn = {
                "accesstoken": accesstoken
            }
        else:
            datareturn = "Failed"
    except Exception as e:
        logging.error("Error: %s", str(e))
    return {
        'statusCode': 200,
        'body': json.dumps(datareturn)
    }
