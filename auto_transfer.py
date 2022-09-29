import json
import os
import sys
from datetime import datetime as dt2
import datetime as dt
sys.path.append("..")
from public.web3_utils import Web3Utils
web3Utils = Web3Utils("https://bsc-dataseed.binance.org/", 5, 56,0)


now_path = os.getcwd()
contract_path = now_path+'/bsc/contract'

with open(contract_path+'/contract.json') as f:
    contract_data = json.load(f)
with open(contract_path+'/account.json') as f:
    account_data = json.load(f)
'''
account_key [str] : Can just pass from metamask private key
'''

account_key = account_data['leo']['key']
account = web3Utils.get_account(account_key)
account_address = account.address





token0 = contract_data['USDT']
token1 = contract_data['ETH']

#  swap method
def Get_Swap_Price(tokenA_address,tokenB_address):
    '''
    tokenA_address [str] : Token Address
    tokenB_address [str] : Token Address
    '''
    factory_contract = web3Utils.w3.eth.contract(address=web3Utils.w3.toChecksumAddress(contract_data['Biswap_factory']['address']), abi=contract_data['Biswap_factory']['ABI'])
    pair_address = factory_contract.functions.getPair(tokenA_address,tokenB_address).call()
    pair_contract = web3Utils.w3.eth.contract(address=web3Utils.w3.toChecksumAddress(pair_address), abi=contract_data['Biswap_pair']['ABI'])
    temp_token0 = pair_contract.functions.token0().call()
    temp_token1 = pair_contract.functions.token1().call()
    pair_rate = pair_contract.functions.getReserves().call()
    return temp_token0,temp_token1 ,pair_rate

def Swap_Token(target,token0,token1):
    '''
    target (int) : Swap USD value
    token0 [Dict] : from contract.json
    token1 [Dict] : from contract.json
    '''
    count = 0
    while count<target:
        print('Now Trading Value = ',count)
        temp_token0,temp_token1,[token0_pool_balance,token1_pool_balance,temp_timestamp] = Get_Swap_Price(token0['address'],token1['address'])
        swap_contract = web3Utils.w3.eth.contract(address=web3Utils.w3.toChecksumAddress(contract_data['Biswap_Swap']['address']), abi=contract_data['Biswap_Swap']['ABI'])
        temp_timestamp = temp_timestamp+700000
        token0_account_balance = int(web3Utils.get_contract_balance(account_address,web3Utils.w3.eth.contract(address=web3Utils.w3.toChecksumAddress(token0['address']), abi=token0['ABI'])))
        token1_account_balance = int(web3Utils.get_contract_balance(account_address,web3Utils.w3.eth.contract(address=web3Utils.w3.toChecksumAddress(token1['address']), abi=token1['ABI'])))
        if temp_token0 != token0['address']:
            if token0_account_balance>0:
                pair_rate = token0_pool_balance/token1_pool_balance
            else:
                pair_rate = token1_pool_balance/token0_pool_balance
        else:
            if token0_account_balance>0:
                pair_rate = token1_pool_balance/token0_pool_balance
            else:
                pair_rate = token0_pool_balance/token1_pool_balance
        
        if token0_account_balance > 0:
            count+=(token0_account_balance/(10**18))
            func = swap_contract.functions.swapExactTokensForTokens(token0_account_balance,int(token0_account_balance*pair_rate*0.9),[token0['address'],token1['address']],account_address,int(temp_timestamp))
        elif token1_account_balance > 0:
            count+=(token1_account_balance*pair_rate/(10**18))
            func = swap_contract.functions.swapExactTokensForTokens(token1_account_balance,int(token1_account_balance*pair_rate*0.9),[token1['address'],token0['address']],account_address,int(temp_timestamp))
        else:
            print('Both Token are Empty')
            break
        account = web3Utils.get_account(account_key)
        nonce = web3Utils.get_nonce(account_address)
        params = {
                    "from": account.address,
                    "value": web3Utils.w3.toWei(0, 'ether'),
                    'gasPrice': web3Utils.gwei,
                    "gas": 500000,
                    "nonce": nonce,
                }
        tx = web3Utils.sign_send(func,params,account_key,'Swap')
        web3Utils.get_receipt_tx(tx)
        nonce+=1



Swap_Token(10000,token0,token1)