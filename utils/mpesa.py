import requests
import base64
from datetime import datetime
import json
from flask import current_app

class MPESAClient:
    """MPESA API client for payment processing"""
    
    def __init__(self):
        self.consumer_key = current_app.config.get('MPESA_CONSUMER_KEY')
        self.consumer_secret = current_app.config.get('MPESA_CONSUMER_SECRET')
        self.shortcode = current_app.config.get('MPESA_SHORTCODE')
        self.passkey = current_app.config.get('MPESA_PASSKEY')
        self.environment = current_app.config.get('MPESA_ENVIRONMENT', 'sandbox')
        
        # Set base URLs based on environment
        if self.environment == 'production':
            self.base_url = 'https://api.safaricom.co.ke'
        else:
            self.base_url = 'https://sandbox.safaricom.co.ke'
    
    def get_access_token(self):
        """Get OAuth access token"""
        url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        
        # Create basic auth header
        credentials = f"{self.consumer_key}:{self.consumer_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            return data.get('access_token')
        
        except requests.exceptions.RequestException as e:
            print(f"Error getting access token: {e}")
            return None
    
    def generate_password(self):
        """Generate password for STK push"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password_string = f"{self.shortcode}{self.passkey}{timestamp}"
        password = base64.b64encode(password_string.encode()).decode()
        
        return password, timestamp
    
    def stk_push(self, phone_number, amount, account_reference, transaction_desc):
        """Initiate STK push payment"""
        access_token = self.get_access_token()
        if not access_token:
            return {'success': False, 'message': 'Failed to get access token'}
        
        password, timestamp = self.generate_password()
        
        url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Format phone number (remove + and ensure it starts with 254)
        if phone_number.startswith('+'):
            phone_number = phone_number[1:]
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        if not phone_number.startswith('254'):
            phone_number = '254' + phone_number
        
        payload = {
            'BusinessShortCode': self.shortcode,
            'Password': password,
            'Timestamp': timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': int(amount),
            'PartyA': phone_number,
            'PartyB': self.shortcode,
            'PhoneNumber': phone_number,
            'CallBackURL': f"{current_app.config.get('BASE_URL', 'http://localhost:5000')}/payments/mpesa/callback",
            'AccountReference': account_reference,
            'TransactionDesc': transaction_desc
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('ResponseCode') == '0':
                return {
                    'success': True,
                    'checkout_request_id': data.get('CheckoutRequestID'),
                    'merchant_request_id': data.get('MerchantRequestID'),
                    'message': 'STK push sent successfully'
                }
            else:
                return {
                    'success': False,
                    'message': data.get('ResponseDescription', 'STK push failed')
                }
        
        except requests.exceptions.RequestException as e:
            print(f"Error initiating STK push: {e}")
            return {'success': False, 'message': 'Network error occurred'}
    
    def query_stk_status(self, checkout_request_id):
        """Query STK push status"""
        access_token = self.get_access_token()
        if not access_token:
            return {'success': False, 'message': 'Failed to get access token'}
        
        password, timestamp = self.generate_password()
        
        url = f"{self.base_url}/mpesa/stkpushquery/v1/query"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'BusinessShortCode': self.shortcode,
            'Password': password,
            'Timestamp': timestamp,
            'CheckoutRequestID': checkout_request_id
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            return data
        
        except requests.exceptions.RequestException as e:
            print(f"Error querying STK status: {e}")
            return {'success': False, 'message': 'Network error occurred'}
    
    def b2c_payment(self, phone_number, amount, occasion, remarks):
        """Business to Customer payment"""
        access_token = self.get_access_token()
        if not access_token:
            return {'success': False, 'message': 'Failed to get access token'}
        
        url = f"{self.base_url}/mpesa/b2c/v1/paymentrequest"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Format phone number
        if phone_number.startswith('+'):
            phone_number = phone_number[1:]
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        if not phone_number.startswith('254'):
            phone_number = '254' + phone_number
        
        payload = {
            'InitiatorName': 'testapi',  # Replace with actual initiator name
            'SecurityCredential': 'your_security_credential',  # Replace with actual credential
            'CommandID': 'BusinessPayment',
            'Amount': int(amount),
            'PartyA': self.shortcode,
            'PartyB': phone_number,
            'Remarks': remarks,
            'QueueTimeOutURL': f"{current_app.config.get('BASE_URL', 'http://localhost:5000')}/payments/mpesa/timeout",
            'ResultURL': f"{current_app.config.get('BASE_URL', 'http://localhost:5000')}/payments/mpesa/result",
            'Occasion': occasion
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            return data
        
        except requests.exceptions.RequestException as e:
            print(f"Error initiating B2C payment: {e}")
            return {'success': False, 'message': 'Network error occurred'}

def process_mpesa_callback(callback_data):
    """Process MPESA callback data"""
    try:
        # Extract relevant information from callback
        stk_callback = callback_data.get('Body', {}).get('stkCallback', {})
        result_code = stk_callback.get('ResultCode')
        result_desc = stk_callback.get('ResultDesc')
        checkout_request_id = stk_callback.get('CheckoutRequestID')
        
        if result_code == 0:  # Success
            # Extract payment details
            callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
            payment_details = {}
            
            for item in callback_metadata:
                name = item.get('Name')
                value = item.get('Value')
                
                if name == 'Amount':
                    payment_details['amount'] = value
                elif name == 'MpesaReceiptNumber':
                    payment_details['receipt_number'] = value
                elif name == 'TransactionDate':
                    payment_details['transaction_date'] = value
                elif name == 'PhoneNumber':
                    payment_details['phone_number'] = value
            
            return {
                'success': True,
                'checkout_request_id': checkout_request_id,
                'payment_details': payment_details,
                'message': 'Payment successful'
            }
        else:
            return {
                'success': False,
                'checkout_request_id': checkout_request_id,
                'message': result_desc or 'Payment failed'
            }
    
    except Exception as e:
        print(f"Error processing MPESA callback: {e}")
        return {
            'success': False,
            'message': 'Error processing callback'
        }
