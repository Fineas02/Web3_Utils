import time
from web3 import Web3
from uniswap import Uniswap
from configparser import ConfigParser
from web3.middleware import geth_poa_middleware

start_time = time.time()

# read config parser
config = ConfigParser()
config.read('config.ini')

# account details section
account = config.get("Account_Details", "account")
private_key = config.get("Account_Details", "private_key")

# rpc connection details
http_rpc_url = config.get("Connection_Details", "http_rpc_url")

# Token details
weth_address = config.get("Token_Details", "weth_address")
usdc_address = config.get("Token_Details", "usdc_address")
ape_address = config.get("Token_Details", "ape_address")

# Uniswap contract details
# V2 Contract
uniswapV2_abi = config.get("Uniswap_Details", "uniswapV2_abi")
uniswapV2_address = config.get("Uniswap_Details", "uniswapV2_address")
# V3 Router 1 Contract
uniswap_R1V3_abi = config.get("Uniswap_Details", "uniswap_R1V3_abi")
uniswap_R1V3_address = config.get("Uniswap_Details", "uniswap_R1V3_address")
# V3 Router 2 Contract
uniswap_R2V3_abi = config.get("Uniswap_Details", "uniswap_R2V3_abi")
uniswap_R2V3_address = config.get("Uniswap_Details", "uniswap_R2V3_address")
# Get Ape to Eth pool
ape_eth_pool = config.get("Uniswap_Details", "ape_eth_pool")

# create an instance of the web3 provider
w3 = Web3(Web3.HTTPProvider(http_rpc_url))

# Uniswap V2 Router Contract
uniswap_contract = w3.eth.contract(uniswapV2_address, abi=uniswapV2_abi)

# Add middleware 
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Get nonce
nonce = w3.eth.get_transaction_count(account)

class UniFunctions:
    # basic web3 function
    def basic_functions():
        print("ETH Block is: ", w3.eth.block_number)
        print("Account_Balance is: ", w3.eth.get_balance(account))
        print("Wei to ETH: ", w3.fromWei(w3.eth.get_balance(account), "ether"))

    def send_eth():
        transaction = {
            "nonce": nonce,
            "to": "0x99373f2D6117bbc43C8f9499353b669Aa42cCab6",
            "value": w3.toWei(0.01, "ether"),
            "gas": 300000,
            "gasPrice": w3.eth.gas_price
        }
        # sign transaction
        signed_trx = w3.eth.account.sign_transaction(transaction, private_key)
        # send transaction
        trx_hash = w3.eth.send_raw_transaction(signed_trx.rawTransaction)
        print("ETH Transaction hash is: ", w3.toHex(trx_hash))
        print("Transaction: ", w3.eth.get_transaction(trx_hash))
        w3.eth.wait_for_transaction_receipt(trx_hash)
        print("Transaction Receipt: ", w3.eth.get_transaction_receipt(trx_hash))

    # Swap for two tokens
    def uniswap_swap():
        # Transaction for token swap
        swap_transaction = uniswap_contract.functions.swapExactETHForTokens(
            0, # minimum amount willing to receive
            [weth_address, usdc_address], # addresses of the tokens for swap
            account, # account to send coins
            int(time.time()) + (60*3) # how long until transaction reverts, currently 3 minutes
        ).buildTransaction({
            "nonce": nonce,
            "gas": 300000,
            "gasPrice": w3.eth.gas_price,
            "from": account,
            "value": w3.toWei(0.01, "ether"),
        })
        # sign transaction
        sign_transaction = w3.eth.account.sign_transaction(swap_transaction, private_key)
        # send transaction
        send_transaction = w3.eth.send_raw_transaction(sign_transaction.rawTransaction)
        # Get hash
        print("Transaction Hash for swap is: ", w3.toHex(send_transaction))

    # Find a transaction by hash function
    def get_transaction():
        # Get transaction
        transaction = w3.eth.get_transaction(0xd2c62d7444d0cf8eab349ae711c1b70a2be69bf5718f681a9ce5f91c75708f5a)
        print(transaction)
        transaction_input = transaction["input"]
        transaction_tag = transaction_input[34:74]
        print("0x" + transaction_tag)

    def search_mempool():
        # Create a list for the mempool
        previous_mempool = []
        # Create a set for transactions
        transaction_hashes = set()

        while True:
            # Get the list of transactions in the mempool
            mempool = w3.eth.getBlock("pending", full_transactions=True)["transactions"]
            # conditional statement to stop loop running forever
            if mempool != previous_mempool:
            # Make a dictionary for transaction 
                transactions = {}
            # Iterate over the transactions and add the relevant ones to the list
                for tx in mempool:
                    
                    # Check if the transaction is relevant to Uniswap
                    if tx["to"] is not None and (tx["to"] in uniswap_R2V3_address or uniswapV2_address or uniswap_R1V3_address) and w3.fromWei(tx['value'], "ether") >= 0.5:
                        # check if transaction is in set to eliminate duplicates
                        if tx["hash"] not in transaction_hashes:
                            # add hash to transaction dictionary
                            transactions[tx['hash']] = w3.fromWei(tx['value'], 'ether')
                
                            # add hash to set
                            transaction_hashes.add(tx['hash'])
                # iterate through transactions
                for hash, value in transactions.items():
                    print("Transaction: ", w3.toHex(hash))
                    print(f"Value: {value} ETH")
                    # get gas price
                    gas_price = w3.eth.gas_price
                    print(gas_price)
                    print()
            previous_mempool = mempool
                        # transaction_cost = tx["value"] * tx["price"]
                        # gas_cost = tx['gas_used'] * gas_price
                        # Uniswap._eth_to_token_swap_input

if __name__ == "__main__":
    # basic_functions()
    # send_eth()
    # uniswap_swap()
    UniFunctions.search_mempool()
    # UniFunctions.get_transaction()




#         # calculate the transaction cost and make sure it is larger than the gas fee
#         transaction_cost = tx['value'] * tx['price']
#         gas_cost = tx['gas_used'] * gas_price
#         if transaction_cost > gas_cost:
#             # buy the token by outbidding the gas fee
#             uniswap._eth_to_token_swap_input(tx['value'], tx['price'], from_= 0x99373f2D6117bbc43C8f9499353b669Aa42cCab6, value = tx['value'] + 5, gas_price=gas_price + 5)

#             # sell the token by underbidding the gas fee
#             uniswap._token_to_eth_swap_input(tx['value'], tx['price'], from_=0x99373f2D6117bbc43C8f9499353b669Aa42cCab6, gas_price=gas_price - 5)