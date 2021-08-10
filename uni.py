import json
from eth_typing.evm import Address
from web3 import Web3
from requests_html import HTMLSession
from discord_webhook import DiscordWebhook
import threading
import sys
import emoji

# global variables
########################################################################
#this is the infura endpoint you get once you sign up at infura.io
#this gives you access to the mainnet
i_url = "https://mainnet.infura.io/v3/1f3e2190cf9a4ad3a67d6eb2f473b1a9"

web3 = Web3(Web3.HTTPProvider(i_url))
session = HTMLSession()

#contract abi
abi = json.loads('[{"inputs":[{"internalType":"address","name":"_feeToSetter","type":"address"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"token0","type":"address"},{"indexed":true,"internalType":"address","name":"token1","type":"address"},{"indexed":false,"internalType":"address","name":"pair","type":"address"},{"indexed":false,"internalType":"uint256","name":"","type":"uint256"}],"name":"PairCreated","type":"event"},{"constant":true,"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"allPairs","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"allPairsLength","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"}],"name":"createPair","outputs":[{"internalType":"address","name":"pair","type":"address"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"feeTo","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"feeToSetter","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"}],"name":"getPair","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"_feeTo","type":"address"}],"name":"setFeeTo","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"_feeToSetter","type":"address"}],"name":"setFeeToSetter","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"}]')
#contract address
address = web3.toChecksumAddress('0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f')
#contract with abi
contract = web3.eth.contract(address=address, abi=abi)
#this is the latest pair created
latest = contract.functions.allPairsLength().call() - 10
#this is the total amount of pairs to date
latest_pair = contract.functions.allPairs(latest).call()
#the url that is used to check the legitimacy of the pair
res_url = f"https://etherscan.io/address/{latest_pair}#notes"
#fetching the above url
r = session.get(res_url)
#tag name from etherscan
value = "#availableBalanceDropdown"
#string search from etherscan
c_res = r.html.search('Uniswap V2 pool to exchange between {} and {}.')

#########################################################################
#main function that controls everything
#########################################################################


def main_func():
    try:
        #v_res comes back as string
        v_res = r.html.find(value, first=True).text
        discord_hook = "https://discord.com/api/webhooks/874035934834880573/Xzrd0iutr4UEEi533ldmio7-ReC8Yk9fpEmD6xfvQNS-mNJEzN7CXeGsmZrqOYik_IS8"

        # this is removing unwanted characters from number returned from the etherscan fetch
        remove_char_step1 = v_res.replace('$', '')
        remove_char_step2 = remove_char_step1.replace('.', '')
        remove_char_step3 = remove_char_step2.replace(',', '')
        l = len(remove_char_step3)
        remove_last = remove_char_step3[:l-1]
        no_lst_num = v_res[:-1]
        new_pair = f'New Pair Created UniswapV2 => %s & %s - %s' % (
            c_res[0], c_res[1], no_lst_num)

        #printing for verification purposes
        print(contract.functions.allPairsLength().call())
        print(latest_pair)

        #logic that checks against previous pair saved
        f = open("address_check.txt", "r")
        last_address = f.readline()

        #if pair saved is not the same as pair fetched then post to discord link
        #if it has no value stop the process and start over
        if last_address != new_pair and int(remove_last) >= 500000:
            print('yes')
            j = open("address_check.txt", "w")
            j.write(f'New Pair Created On UniswapV2 => %s & %s - %s' %
                    (c_res[0], c_res[1], no_lst_num))
            j.close()
            webhook = DiscordWebhook(url=discord_hook, rate_limit_retry=True, content=emoji.emojize(f':fire: :fire: :fire: New Pair Created On UniswapV2 => %s & %s - %s' % (c_res[0], c_res[1], no_lst_num)))
            response = webhook.execute()

        print(f'New Pair Created On UniswapV2 => %s & %s - %s' %
              (c_res[0], c_res[1], no_lst_num))

    except:
        sys.exit()


#class keeps calling the main function
class ThreadJob(threading.Thread):
    def __init__(self, callback, event, interval):
        '''runs the callback function after interval seconds

        :param callback:  callback function to invoke
        :param event: external event for controlling the update operation
        :param interval: time in seconds after which are required to fire the callback
        :type callback: function
        :type interval: int
        '''
        self.callback = callback
        self.event = event
        self.interval = interval
        super(ThreadJob, self).__init__()

    def run(self):
        while not self.event.wait(self.interval):
            self.callback()


event = threading.Event()

#change 3600 to the number of seconds you want
k = ThreadJob(main_func, event, 3600)
k.start()
