import requests

# Replace with your actual Store ID and Store Password
store_id = "techh6832b3ae538f2"
store_password = "techh6832b3ae538f2@ssl"

# SSLCommerz API endpoint (sandbox URL)
url = "https://sandbox.sslcommerz.com/gwprocess/v4/api.php"



# Updated payload with 'product_name'
payload = {
    "store_id": store_id,
    "store_passwd": store_password,
    "total_amount": 10,
    "currency": "BDT",
    "tran_id": "test_transaction_123",
    "success_url": "https://example.com/success",
    "fail_url": "https://example.com/fail",
    "cancel_url": "https://example.com/cancel",
    "cus_name": "Test User",
    "cus_email": "test@example.com",
    "cus_add1": "Dhaka",
    "cus_city": "Dhaka", 
    "cus_postcode": "1212", 
    "cus_country": "Bangladesh",
    "cus_phone": "01700000000",
    "product_category": "Electronics",
    "product_name": "Computer, Speaker",
    "shipping_method": "Courier",
    "num_of_item": 2,
    "ship_name": "Test User",
    "ship_add1": "Dhaka",
    "ship_city": "Dhaka",
    "ship_postcode": "1212",
    "ship_country": "Bangladesh",
    'product_profile': 'None', 
}

# Send POST request to test connection
response = requests.post(url, data=payload)

# Print the response from SSLCommerz
print("Status Code:", response.status_code)
print("Response:", response.json())