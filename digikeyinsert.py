from requests.api import get
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
from requests.api import get, post
import urllib.parse

def Digikeyinsert(event, context):
    try:
        postdata = json.loads(event['body'])
        import uuid
        uuidx = uuid.uuid4()
        uuid1 = str(uuidx)
        uuid2 = uuid1.replace('-', '')
        uuid2 = uuid2[-25:]
        qrcode = postdata['qrcode']
        logging.info(qrcode)
        accesstoken = postdata['accesstoken']
        currentUser = postdata['currentUser']
        digi_headers = {
            "X-DIGIKEY-Client-Id": "LttNhtAWuhAxykn3fDdkrvOaAWgDUXro",
            'authorization': "Bearer " + accesstoken,
            'accept': "application/json"
        }
        urlencode = urllib.parse.quote(qrcode, safe=')')
        url = "https://api.digikey.com/Barcoding/v3/Product2DBarcodes/" + urlencode
        postqrcode = requests.get( url, headers=digi_headers)
        logging.info(postqrcode.json())
        if (postqrcode.status_code == 200):
            getpostdatadir = json.dumps(postqrcode.json())
            getpostdataloads = json.loads(getpostdatadir)

            getperson = requests.get(
                '/'+currentUser+'.json')
            getpersondir = json.dumps(getperson.json())
            getpersonloads = json.loads(getpersondir)
            preferred_4x6_printer = getpersonloads['preferred_4x6_printer']

            datapatch = {
                "description": getpostdataloads['ProductDescription'],
                "name": getpostdataloads['ManufacturerPartNumber'],
                "part_number": getpostdataloads['DigiKeyPartNumber'],
                "uuid": uuid2
            }
            patchdatapatch = requests.patch(
                '/'+uuid2+'.json', json=datapatch)
            createpdf = {
                'html': f"""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Label single</title>
                <style>
                    body, html {{
                    margin: 0;
                    padding: 0;
                    font-size: 10px;
                    font-family: sans-serif;
                    }}
                    .container {{
                    width: 2.625in;
                    height: 1in;
                    }}
                    .container:nth-child(2n), .container:nth-child(3n) {{
                    page-break-before: always;
                    }}
                    .label-root {{
                    display: inline-block;
                    width: 2.555in;
                    height: 0.93in;
                    padding: 0.035in;
                    }}
                    .label-root p {{
                    margin: 0;
                    }}
                    .label-root .qr-code-wrapper {{
                    float: left;
                    width: 0.83in;
                    line-height: 0;
                    margin-right: 0.07in;
                    }}
                    .label-root .details-wrapper {{
                    }}
                    .qr-code-wrapper .qr-code {{
                    max-width: 100%;
                    }}
                    .details-wrapper .label-meta {{
                    margin-right: 0.07in;
                    margin-bottom: 0.07in;
                    }}
                    .label-meta .icon {{
                    display: inline-block;
                    max-width: 32px;
                    max-height: 32px;
                    vertical-align: middle;
                    margin-right: 0.035in;
                    }}
                    .label-meta p {{
                    display: inline;
                    }}
                    .details-wrapper .label-info {{
                    overflow: hidden;
                    }}
                    .label-info .title {{
                    font-weight: 700;
                    margin-bottom: 0.035in;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    }}
                    .label-info .subtitle {{
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    }}
                    .label-root .label-footer {{
                    clear: both;
                    font-size: 8px;
                    letter-spacing: 1px;
                    line-height: 0.1in;
                    padding-left: 0.035in;
                    height: 0.1in;
                    }}
                </style>
                </head>
                <body>
                <div class="container">
                    <!-- BEGIN: Label -->
                    <div class="label-root">
                    <div class="qr-code-wrapper">
                        <img src="https://api.3hd.us/app/qrcode_gen.create?data=3hd.us/{uuid2}&logo=momenttrack" class="qr-code"/>
                    </div>
                    <div class="details-wrapper">
                        <div class="label-meta">
                        <img src="https://replenish-icons.s3-us-west-1.amazonaws.com/current_icons/licence_plate_icon.svg" class="icon">
                        <p><small><b>PO:</b> {getpostdataloads['DigiKeyPartNumber']}</small></p>
                        </div>
                        <div class="label-info">
                        <p class="title">{getpostdataloads['ManufacturerPartNumber']}</p>

                        <p class="subtitle"><b>Qty:</b> {getpostdataloads['Quantity']}</p>
                        </div>
                    </div>
                    <p class="label-footer">3hd.us/{uuid2}</p>
                    </div>
                    <!-- END: Label -->
                </div>
                </body>
                </html>
                    """,
                "pdf_mode": "portrait",
                "pdf_name": uuid2,
                "page_width": '66.675mm',
                "page_height": '25.4mm',
                "margin_top": '0mm',
                "margin_bottom": '0mm',
                "margin_left": '0mm',
                "margin_right": '0mm',
                'disable_smart_shrinking': ''
            }
            createpdfpost = requests.post(
                '/html2pdf.generate_pdf', json=createpdf)
            json_dictionary = json.dumps(createpdfpost.json())
            red = json.loads(json_dictionary)
            data1 = red['data']
            data11 = data1['s3_path']

            printpdf = {
                "printer_url": preferred_4x6_printer,
                "title": "Print Label",
                "contentType": "pdf_uri",
                "content": data11,
                "expireAfter": 600,
                "passkey": "jaredeggettiscool"
            }
            printpdff = requests.post(
                '', json=printpdf)
            datareturn = 'success'
            logging.info(data11)
        else:
            datareturn = 'failed'

    except Exception as e:
        logging.error("Error: %s", str(e))
    return {
        'statusCode': 200,
        'body': json.dumps(datareturn)
    }
