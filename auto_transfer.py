import json
import os
import sys
from datetime import datetime as dt2
import datetime as dt

sys.path.append("..")
from public.web3_utils import Web3Utils
web3Utils = Web3Utils("https://bsc-dataseed.binance.org/", 5, 56,0)
'''
account_address 交易地址
account_key key
'''
# with open(contract_path+'/contract.json', 'w') as fp:
#     json.dump(data, fp)
now_path = os.getcwd()
contract_path = now_path+'/bsc/contract'
with open(contract_path+'/contract.json') as f:
    contract_data = json.load(f)
with open(contract_path+'/account.json') as f:
    account_data = json.load(f)
account_address = account_data['leo']['address']
account_key = account_data['leo']['key']
nonce = web3Utils.get_nonce(account_address)


#  swap method
def Get_Swap_Price(tokenA_address,tokenB_address):
    factory_contract = web3Utils.w3.eth.contract(address=web3Utils.w3.toChecksumAddress(contract_data['Biswap_factory']['address']), abi=contract_data['Biswap_factory']['ABI'])
    pair_address = factory_contract.functions.getPair(tokenA_address,tokenB_address).call()
    pair_contract = web3Utils.w3.eth.contract(address=web3Utils.w3.toChecksumAddress(pair_address), abi=contract_data['Biswap_pair']['ABI'])
    token0 = pair_contract.functions.token0().call()
    token1 = pair_contract.functions.token1().call()
    pair_rate = pair_contract.functions.getReserves().call()
    return token0,token1 ,pair_rate

'''
test dict save to json
'''





token0,token1,[token0_balance,token1_balance,temp_timestamp] = Get_Swap_Price(contract_data['ETH']['address'],contract_data["BUSD"]['address'])

count = 0
target = 1000
while count<target:
    print('count=',count)
    swap_contract = web3Utils.w3.eth.contract(address=web3Utils.w3.toChecksumAddress(contract_data['Biswap_Swap']['address']), abi=contract_data['Biswap_Swap']['ABI'])
    temp_timestamp = temp_timestamp+700000
    usdt_balance = int(web3Utils.get_contract_balance(account_address,web3Utils.w3.eth.contract(address=web3Utils.w3.toChecksumAddress(contract_data['USDT']['address']), abi=contract_data['USDT']['ABI'])))
    eth_balance = int(web3Utils.get_contract_balance(account_address,web3Utils.w3.eth.contract(address=web3Utils.w3.toChecksumAddress(contract_data['ETH']['address']), abi=contract_data['ETH']['ABI'])))


    if usdt_balance > 0:
        count+=(usdt_balance/(10**18))
        pair_rate = token0_balance/token1_balance
        func = swap_contract.functions.swapExactTokensForTokens(usdt_balance,int(usdt_balance*pair_rate*0.9),[contract_data['USDT']['address'],contract_data['ETH']['address']],account_address,int(temp_timestamp))
    elif eth_balance > 0:
        pair_rate = (token1_balance/token0_balance)
        allow_balance = eth_balance
        count+=(eth_balance*pair_rate/(10**18))
        func = swap_contract.functions.swapExactTokensForTokens(allow_balance,int(allow_balance*pair_rate*0.9),[contract_data['ETH']['address'],contract_data['USDT']['address']],account_address,int(temp_timestamp))
    else:
        print('No ',token0,'No ',token1)
    account = web3Utils.get_account(account_key)
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
