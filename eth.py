import requests
import json
import threading

class Account:
    
    def __init__(self):
        self.file_name = "wallets.txt"
        self.acc_list = []
        
    def read(self):
        with open(self.file_name, "r") as reader:
            contents = reader.read()
            self.acc_list = contents.split(",")
        return self.acc_list
    
    def write(self):
        with open(self.file_name, 'w') as writer:
            for i in self.acc_list:
                writer.write(",{}".format(i))
                
    def add(self, wallet_hash):
        self.acc_list.append(wallet_hash)
        self.write()
        self.read()
                
class Log:
    
    def __init__(self):
        self.file_name = "logs.txt"
        self.logs = self.read()
       
    def read(self):
        with open(self.file_name, "r") as json_file:
            data = json.load(json_file)
        return data
        
    def append(self, to, transaction, value, status):
        data = {
            "to": to,
            "transaction":transaction,
            "sum": value,
            "status": status
        }
        self.logs["transactions"].append(data)
        self.save()
        
    def save(self):
       
        with open('logs.txt', 'w') as outfile:
            json.dump(self.logs, outfile)
        
    def out(self):
        print(self.logs)


class Watcher:
    
    def __init__(self):
        
        self.account = Account()
        self.watch_list = self.account.read()
        self.last_block_checked = self.get_last_block()
        self.current_last_block = self.last_block_checked
        self.logs = Log()
    
    def update_watchList(self):

        self.watch_list = self.account.read()
        

    def generate_request(self, method, params = []):
        
        data = {
            "jsonrpc":"2.0",
            "method": method,
            "params": params,
            "id":1
        }
        return json.dumps(data)
    
    def make_request(self, method, params = []):
        
        headers = {
            'Content-Type': 'application/json',
        }

        data = self.generate_request(method, params)
        response = requests.post('https://mainnet.infura.io/v3/b505508da0d847f59fea17958894a9bc',\
                             headers=headers, data=data)
        return json.loads(response.text)
    
    def get_last_block(self):
        
        a = self.make_request("eth_blockNumber")["result"]
        return int(a, 0)
    
        
    def check_for_transactions_in_block(self, block_id):
        
        hexed_block_id = hex(block_id)
        block = self.make_request("eth_getBlockByNumber", [str(hexed_block_id), True])
        for transaction in block["result"]["transactions"]:
            if transaction["to"] in self.watch_list:
                
                status = self.get_Receipt(transaction["hash"])
                self.logs.append(transaction["to"], transaction["hash"], transaction["value"], "0x1")
                
    def get_Receipt(self, hashed):
        
        return self.make_request("eth_getTransactionReceipt", [hashed])["result"]["status"]
    
    def check_last(self):

        print("cc")
        self.current_last_block = self.get_last_block()
        if self.last_block_checked == self.current_last_block:
            return

        for i in range(self.last_block_checked, self.current_last_block):
            print(self.last_block_checked, self.current_last_block)
            self.last_block_checked = i
            self.check_for_transactions_in_block(i)
            
            
    def begin_loop(self):
        try:
            self.check_last()
        except:
            self.check_last()
        threading.Timer(10.0, self.begin_loop).start()


    def start(self):

        self.logs.read()
        self.account.read()
        print("STARTING....")
        self.begin_loop()
