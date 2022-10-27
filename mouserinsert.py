import re
import requests
import json
import logging


def Mouserinsert(event, context):
    try:
        postdata = json.loads(event['body'])
        import uuid
        uuidx = uuid.uuid4()
        uuid1 = str(uuidx)
        uuid2 = uuid1.replace('-', '')
        uuid2 = uuid2[-25:]
        qrcode = str(postdata['qrcode'])
        currentUser = postdata['currentUser']
        split_mouserstrings = '''\
        >[)>06K
        14K
        P
        Q
        11K
        4L
        1V
        '''.splitlines()
        rexp = re.compile('|'.join(re.escape(x) for x in split_mouserstrings))
        result = rexp.split(qrcode)
        logging.info(result)
        Cust_PO = ""
        Line_Item = ""
        Cust_PN = ""
        Qty = ""
        unkownitem1 = ""
        CityOrigin = ""
        Desc = ""

        getitempart = 0
        for result1 in result:
            getitempart = getitempart + 1
            if getitempart == 1:
                Cust_PO = result1[7:]
                print(Cust_PO)
            elif getitempart == 2:
                Line_Item = result1
                print(Line_Item)
            elif getitempart == 3:
                Cust_PN = result1
                print(Cust_PN)
            elif getitempart == 4:
                Qty = result1
                print(Qty)
            elif getitempart == 5:
                unkownitem1 = result1
                print(unkownitem1)
            elif getitempart == 6:
                CityOrigin = result1
                print(CityOrigin)
            elif getitempart == 7:
                Desc = result1
                print(Desc)

        rx = re.compile('\x1d')
        Cust_PO2 = rx.sub('', Cust_PO).strip()
        Line_Item2 = rx.sub('', Line_Item).strip()
        Cust_PN2 = rx.sub('', Cust_PN).strip()
        Qty2 = rx.sub('', Qty).strip()
        unkownitem12 = rx.sub('', unkownitem1).strip()
        CityOrigin2 = rx.sub('', CityOrigin).strip()
        Desc2 = rx.sub('', Desc).strip()

        getperson = requests.get(
            '/access_rights/'+currentUser+'.json')
        getpersondir = json.dumps(getperson.json())
        getpersonloads = json.loads(getpersondir)
        company_code = getpersonloads['company_code']
        preferred_4x6_printer = getpersonloads['preferred_4x6_printer']

        datapatch = {
            "company": company_code,
            "type": 'Mouser',
            "PO_num": Cust_PO2,
            "city_origin": CityOrigin2,
            "Qty": Qty2,
            "id": uuid2,
            "licence_plate": "3hd.us/" + uuid2,
            "manufacturer_part_number": Cust_PN2,
            "Invoice": unkownitem12,
            "Desc": Desc2,

        }
        patchdatapatch = requests.patch(
            'licence_plate/'+uuid2+'.json', json=datapatch)
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
            <p><small><b>PO:</b> {Cust_PN2}</small></p>
            </div>
            <div class="label-info">
            <p class="title">{Cust_PO2}</p>

            <p class="subtitle"><b>Qty:</b> {Qty2}</p>
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
        createpdfpost = requests.post(
            'https://x7jjoqcd0h.execute-api.us-west-1.amazonaws.com/beta/convert', json=createpdf)
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
            'https://k2vpki1p5i.execute-api.us-west-1.amazonaws.com/prod/printNode', json=printpdf)
        logging.info(data11)

    except Exception as e:
        logging.error("Error: %s", str(e))
    return {
        'statusCode': 200,
        'body': 'success'
    }
