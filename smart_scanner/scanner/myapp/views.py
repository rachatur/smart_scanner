import os
from django.shortcuts import render
import qrcode
from requests.auth import HTTPBasicAuth
import requests
from django.http import JsonResponse
from datetime import datetime
from . import models


GET_URL = "https://edrx-dev1.fa.us2.oraclecloud.com/fscmRestApi/resources/11.13.18.05/itemsV2"
POST_URL = "https://edrx-dev1.fa.us2.oraclecloud.com/fscmRestApi/resources/latest/availableQuantityDetails"
AUTH = HTTPBasicAuth('CSP_COMMON_USER1', 'CSP@Jul240704')


def item_list(request):
    items_model = models.Item.objects.all()
    return render(request, 'myapp/item_list.html', {'items_model': items_model})

 
def home(request):
    # Get data from session
    get_data = request.session.get('get_data', None)

    get_params = {
        'q': 'OrganizationCode=MFG01'
    }

    try:
        response = requests.get(GET_URL, params=get_params, auth=AUTH)
        response.raise_for_status()
        updated_get_data = response.json()
        request.session['get_data'] = updated_get_data  # Update session data
    except requests.exceptions.RequestException as e:
        # Handle API request errors
        updated_get_data = None

    return render(request, 'myapp/home.html', {'get_data': get_data or updated_get_data})


def fetch_external_data(request):
    if request.method == 'GET':
        item_number = request.GET.get('item_number')
        if not item_number:
            return JsonResponse({'error': 'Item number is required'}, status=400)

        request.session['item_number'] = item_number

        # GET API
        get_params = {
            'q': f'ItemNumber={item_number};OrganizationCode=MFG01'
        }

        try:
            response = requests.get(GET_URL, params=get_params, auth=AUTH)
            response.raise_for_status()
            get_single_data = response.json()
        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)

        # POST API
        post_data = {
            'ItemNumber': item_number,
            'OrganizationCode': 'MFG01'
        }

        try:
            response = requests.post(POST_URL, json=post_data, auth=AUTH)
            response.raise_for_status()
            post_response = response.json()
        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)

        return render(request, 'myapp/item_list_transaction.html', {
            'get_response': get_single_data,
            'post_response': post_response,
        })

    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


def item_page(request):
    item_number = request.session.get('item_number', '')

    get_params = {
        'q': f'ItemNumber={item_number};OrganizationCode=MFG01'
    }

    try:
        response = requests.get(GET_URL, params=get_params, auth=AUTH)
        response.raise_for_status()
        get_single_data = response.json()
        # Assuming get_single_data contains the necessary information to display subinventory options
        # request.session['get_data'] = get_single_data  # Update session data
        # print(get_single_data)  # Debugging line to verify the data
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)

    return render(request, 'myapp/item_page.html', {
        'item_number': item_number, 'get_single_data': get_single_data})
        # , 'post_response': post_response})


def fetch_inventory(request):
    today = datetime.today()

    if request.method == 'POST':
        item_number = request.session.get('item_number', '')
        item = item_number
        quantity = request.POST.get('quantity')
        subinventory_code = request.POST.get('subinventory_code')
        transfer_subinventory_code = request.POST.get('transfer_subinventory_code')

        username = os.getenv('CSP_USERNAME', 'CSP_COMMON_USER1')
        password = os.getenv('CSP_PASSWORD', 'CSP@Jul240704')
        auth = HTTPBasicAuth(username, password)

        # POST API call details
        post_url = ("https://edrx-dev1.fa.us2.oraclecloud.com/fscmRestApi/resources/11.13.18.05"
                    "/inventoryStagedTransactions")
        post_data = {
            "OrganizationName": "OPM Inventory Organization 01",
            "TransactionTypeName": "Subinventory Transfer",
            "ItemNumber": item,
            "TransactionQuantity": quantity,
            "TransactionUnitOfMeasure": "Ea",
            "TransactionDate": today.strftime('%Y-%m-%d'),
            "SubinventoryCode": subinventory_code,
            "TransferSubinventory": transfer_subinventory_code,
            "SourceCode": "RS",
            "SourceLineId": "1",
            "SourceHeaderId": "1",
            "TransactionMode": "1",
            "TransactionReference": "MMJ100",
            "UseCurrentCostFlag": "true"
        }

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
                'TransferSubinventory': post_response_data.get('TransferSubinventory', ''),
                'item_number': item_number
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


def base(request):
    return render(request, 'base.html')


# def inventory(request):
#     return render(request, 'myapp/item_page.html')


# def get_data(request):
#     # Get all items API
#     get_params = {
#         'q': f'OrganizationCode=MFG01'
#     }
#
#     try:
#         response = requests.get(GET_URL, params=get_params, auth=AUTH)
#         response.raise_for_status()
#         get_data2 = response.json()
#     except requests.exceptions.RequestException as e:
#         return JsonResponse({'error': str(e)}, status=500)
#     return render(request, 'myapp/home.html', {'get_data2': get_data2})


