import os
from django.shortcuts import render
import qrcode
from requests.auth import HTTPBasicAuth
import requests
from django.http import JsonResponse


def home(request):
    return render(request, 'myapp/home.html')


def fetch_external_data(request):

    if request.method == 'GET':
        item_number = request.GET.get('item_number')
        if not item_number:
            return JsonResponse({'error': 'Item number is required'}, status=400)

        # GET API call
        get_url = "https://edrx-dev1.fa.us2.oraclecloud.com/fscmRestApi/resources/11.13.18.05/itemsV2"
        get_params = {
            'q': f'ItemNumber={item_number};OrganizationCode=MFG01'
        }
        auth = HTTPBasicAuth('CSP_COMMON_USER1', 'CSP@0524May')

        try:
            response = requests.get(get_url, params=get_params, auth=auth)
            response.raise_for_status()
            get_data = response.json()

        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)

        # POST API call
        post_url = "https://edrx-dev1.fa.us2.oraclecloud.com/fscmRestApi/resources/latest/availableQuantityDetails"
        post_data = {
            'ItemNumber': item_number,
            'OrganizationCode': 'MFG01'
        }

        try:
            response = requests.post(post_url, json=post_data, auth=auth)
            response.raise_for_status()
            post_data = response.json()
            # print(post_data)

        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)

        return render(request, 'myapp/information.html', {'get_response': get_data, 'post_response': post_data})

    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


def inventory(request):
    return render(request, 'myapp/item_page.html')


def fetch_inventory(request):
    if request.method == 'POST':

        item = request.POST.get('item')
        quantity = request.POST.get('quantity')
        subinventory_code = request.POST.get('subinventory_code')
        transfer_subinventory_code = request.POST.get('transfer_subinventory_code')


        username = os.getenv('CSP_USERNAME', 'CSP_COMMON_USER1')
        password = os.getenv('CSP_PASSWORD', 'CSP@0524May')
        auth = HTTPBasicAuth(username, password)

        # POST API call details
        post_url = "https://edrx-dev1.fa.us2.oraclecloud.com/fscmRestApi/resources/11.13.18.05/inventoryStagedTransactions"
        post_data ={
          "OrganizationName": "OPM Inventory Organization 01",
          "TransactionTypeName": "Subinventory Transfer",
          "ItemNumber": item,
          "TransactionQuantity": quantity,
          "TransactionUnitOfMeasure": "Ea",
          "TransactionDate": "2024-06-07 10:04:55.000000000",
          "SubinventoryCode": subinventory_code,
          "TransferSubinventory": transfer_subinventory_code,
          "SourceCode": "RS",
          "SourceLineId": "1",
          "SourceHeaderId": "1",
          "TransactionMode": "1",
          "TransactionReference": "MMJ100",
          "UseCurrentCostFlag": "true"
        }


        #     {
        #     "OrganizationName": "MFG01",
        #     "TransactionTypeName": "Subinventory Transfer",
        #     "ItemNumber": item,
        #     "TransactionQuantity": quantity,
        #     "TransactionUnitOfMeasure": "Ea",
        #     "TransactionDate": "2024-06-07 10:04:55.000000000",
        #     "SubinventoryCode": subinventory_code,
        #     "TransferSubinventory": transfer_subinventory_code,
        #     "SourceCode": "RS",
        #     "SourceLineId": "1",
        #     "SourceHeaderId": "1",
        #     "TransactionMode": "1",
        #     "TransactionReference": "MMJ100",
        #     "UseCurrentCostFlag": "true"
        # }

        try:
            response = requests.post(post_url, json=post_data, auth=auth)
            response.raise_for_status()
            post_response_data = response.json()

            print("POST request successful:", post_response_data)

        except requests.exceptions.RequestException as e:

            print("POST request failed:", e)
            return JsonResponse({'error': str(e)}, status=500)

        context = {
            'post_response': {
                'ItemNumber': post_response_data.get('ItemNumber', ''),
                'TransactionQuantity': post_response_data.get('TransactionQuantity', ''),
                'SubinventoryCode': post_response_data.get('SubinventoryCode', ''),
                'TransferSubinventory': post_response_data.get('TransferSubinventory', '')
            }
        }

        return render(request, 'myapp/subinventory_data.html', context)

    return render(request, 'myapp/form.html')

def generate_qr(request):
    data = 'MANGOMAZZA200ML'

    # qr_code_directory = os.path.join(settings.BASE_DIR, 'myapp', 'templates', 'images')
    qr_code_directory = os.path.join('static/img')
    if not os.path.exists(qr_code_directory):
        os.makedirs(qr_code_directory)

    QRCodefile = os.path.join(qr_code_directory, 'first.png')

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    QrImage = qr.make_image(fill='black', back_color='white')
    QrImage.save(QRCodefile)

    context = {
        'qr_code_url': 'images/first.png'
    }
    return render(request, 'myapp/qr.html', context)
