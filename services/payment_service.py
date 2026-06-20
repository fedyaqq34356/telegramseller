import aiohttp
from config.settings import CRYPTO_BOT_TOKEN, CRYPTO_BOT_API_URL


class CryptoPayAPI:
    def __init__(self):
        self.api_url = CRYPTO_BOT_API_URL
        self.token = CRYPTO_BOT_TOKEN
        self.headers = {
            'Crypto-Pay-API-Token': self.token,
            'Content-Type': 'application/json'
        }
    
    async def create_invoice(
        self,
        amount: float,
        asset: str = 'USDT',
        description: str = '',
        payload: str = ''
    ):
        url = f"{self.api_url}/createInvoice"
        
        data = {
            'currency_type': 'crypto',
            'asset': asset,
            'amount': str(amount),
            'description': description,
            'payload': payload
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.headers, json=data) as response:
                result = await response.json()
                if result.get('ok'):
                    return result['result']
                return None
    
    async def get_invoice(self, invoice_id: int):
        url = f"{self.api_url}/getInvoices"
        
        params = {
            'invoice_ids': str(invoice_id)
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers, params=params) as response:
                result = await response.json()
                if result.get('ok') and result.get('result'):
                    return result['result'][0]
                return None
    
    async def check_invoice_paid(self, invoice_id: int) -> bool:
        invoice = await self.get_invoice(invoice_id)
        if invoice:
            return invoice.get('status') == 'paid'
        return False


crypto_pay = CryptoPayAPI()