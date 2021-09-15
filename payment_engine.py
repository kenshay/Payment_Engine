import copy
import csv
import os
import sys
u16 = 65535
u32 = 4294967295

def isDebug():
    try:
        DebugFlag = sys.argv[2]
        if DebugFlag == '-d':
            Debug = True
        else:
            Debug = False
    except:
        Debug = False
    return Debug


class Payment_Engine_Class():
    def __init__(self,transactions_csv,isDebug=False):
        self.isDebug = isDebug
        self.transactions_csv = os.path.abspath(transactions_csv)


    def truncate_float(self,num):
        n = 4
        num = float(num)
        integer = int(num * (10 ** n)) / (10 ** n)
        the_float = float(integer)
        if the_float == 0.0:
            the_float = 0
        return the_float

    def debug_print(self,x):
        if self.isDebug == True:
            print(x)
            print('\n')

    def insure_only_one_of_each_account(self,client_accounts_list):
        client_accounts_list = list(set(client_accounts_list))
        return client_accounts_list

    def find_transcaction(self,tx):
        with open(self.transactions_csv, 'r') as transactions_csv:
            csv_reader = csv.reader(transactions_csv)
            next(csv_reader)
            for transaction in csv_reader:
                transaction_dict = {}
                transaction_dict['tx'] = int(transaction[2])
                transaction_dict['type'] = str(transaction[0])
                if transaction_dict['tx'] == tx:
                    if transaction_dict['type'] not in ['dispute','resolve','chargeback']:
                        transaction_dict['client'] = int(transaction[1])
                        if transaction[3] == '':
                            transaction[3] = 0
                        transaction_dict['amount'] = float(transaction[3])
                        return transaction_dict
        return False


    def isTXUnderDispute(self,tx):
        if tx not in self.resolved_transactions:
            with open(self.transactions_csv, 'r') as transactions_csv:
                csv_reader = csv.reader(transactions_csv)
                next(csv_reader)
                for transaction in csv_reader:
                    transaction_dict = {}
                    transaction_dict['tx'] = int(transaction[2])
                    transaction_dict['type'] = str(transaction[0])
                    if transaction_dict['tx'] == tx:
                        if transaction_dict['type'] == 'dispute':
                            return True
        return False


    def negatives_in_data(self,available,held,total):
        #Checks for negatives
        if available < 0:
            return True
        if held < 0:
            return True
        if total < 0:
            return True
        return False


    def check_data(self,available,held,total):
        #The total funds that are available for trading, staking, withdrawal, etc. This should be #equal to the total - held amounts
        Bool = total - held == available
        if Bool == False:
            raise Exception('total - held != available!')

        #The total funds that are held for dispute. This should be equal to total - available amounts
        Bool = total - available == held
        if Bool == False:
            raise Exception('total - available != held!')

        #The total funds that are available or held. This should be equal to available + held
        Bool = available + held == total
        if Bool == False:
            raise Exception('available + held != total!')


    def deposit(self,transaction_dict,client_dict):
        client_dict = copy.copy(client_dict) #Ensure Fake Copy
        #A deposit is a credit to the client's asset account.

        self.debug_print('#######################################')
        self.debug_print('Before Deposit-> ' + str(client_dict))

        # It should increase the available and total funds of the client account A
        self.debug_print('Total + ' + str(transaction_dict['amount']))
        client_dict['total'] += transaction_dict['amount']
        self.debug_print('Available + ' + str(transaction_dict['amount']))
        client_dict['available'] += transaction_dict['amount']

        self.check_data(client_dict['available'], client_dict['held'], client_dict['total'])
        if self.negatives_in_data(client_dict['available'], client_dict['held'], client_dict['total']) == False:
            self.client_accounts_dict[transaction_dict['client']] = client_dict
            self.debug_print('After  Deposit-> ' + str(client_dict))
        else:
            self.debug_print(
                "Negative Number Found! " + str(client_dict['available']) + ',' + str(client_dict['held']) + ',' + str(
                    client_dict['total']) + " Skipping Transaction")
            self.debug_print('After  Deposit-> ' + str(self.client_accounts_dict[transaction_dict['client']]))



    def withdrawal(self, transaction_dict, client_dict):
        client_dict = copy.copy(client_dict) #Ensure Fake Copy

        # A withdraw is a debit to the client's asset account.

        self.debug_print('#######################################')
        self.debug_print('Before Withdrawel-> ' + str(client_dict))
        if client_dict['available'] >= transaction_dict['amount']:

            # It should decrease the available and total funds of the client account A
            self.debug_print('Total - ' + str(transaction_dict['amount']))
            client_dict['total'] -= transaction_dict['amount']
            self.debug_print('Available - ' + str(transaction_dict['amount']))
            client_dict['available'] -= transaction_dict['amount']

            self.check_data(client_dict['available'], client_dict['held'], client_dict['total'])
            if self.negatives_in_data(client_dict['available'], client_dict['held'], client_dict['total']) == False:
                self.client_accounts_dict[transaction_dict['client']] = client_dict
                self.debug_print('After  Withdrawel-> ' + str(client_dict))
            else:
                self.debug_print(
                    "Negative Number Found! " + str(client_dict['available']) + ',' + str(
                        client_dict['held']) + ',' + str(
                        client_dict['total']) + " Skipping Transaction")
                self.debug_print('After  Withdrawel-> ' + str(self.client_accounts_dict[transaction_dict['client']]))


        else:
            # If a client does not have sufficient available funds the withdrawal should fail and the total amount of funds should not change.
            self.debug_print('Inusufficiant funds! Skipping Transaction.')
            self.debug_print('After  Withdrawel-> ' + str(client_dict))



    def dispute(self, transaction_dict, client_dict):
        client_dict = copy.copy(client_dict) #Ensure Fake Copy
        # A dispute represents a client's claim that a transaction was erroneous and should be reverse.
        # The transaction shouldn't be reversed yet but the associated funds should be held.
        # Notice that a dispute does not state the amount disputed.
        # Instead a dispute references the transaction that is #disputed by ID.

        self.debug_print('#######################################')
        self.debug_print('Before Dispute->' + str(client_dict))

        x = transaction_dict['tx']
        transaction = self.find_transcaction(x)
        if transaction != False:
            # This means that the clients available funds should decrease by the amount disputed,
            # their held funds should increase by the amount disputed,
            # while their total funds should remain the same.
            self.debug_print('Transaction = ' + str(transaction))

            past_amount = transaction['amount']
            self.debug_print('Past Amount = ' + str(past_amount))


            self.debug_print('Available - ' + str(past_amount))
            client_dict['available'] -= past_amount

            self.debug_print('Held + ' + str(past_amount))
            client_dict['held'] += past_amount

            self.check_data(client_dict['available'], client_dict['held'], client_dict['total'])
            if self.negatives_in_data(client_dict['available'], client_dict['held'], client_dict['total']) == False:
                self.client_accounts_dict[transaction_dict['client']] = client_dict
                self.debug_print('After Dispute->' + str(client_dict))
            else:
                self.debug_print(
                    "Negative Number Found! " + str(client_dict['available']) + ',' + str(
                        client_dict['held']) + ',' + str(
                        client_dict['total']) + " Skipping Transaction")
                self.debug_print('After Dispute->' + str(self.client_accounts_dict[transaction_dict['client']]))


        else:
            # If the tx specified by the dispute doesn't exist you can ignore it and assume this is an error on our partners side.
            self.debug_print('Transaction -> ' + str(x) + ' Doesnt Exist! Skipping Transaction.')
            self.debug_print('After  Dispute-> ' + str(client_dict))


    def resolve(self, transaction_dict, client_dict):
        client_dict = copy.copy(client_dict) #Ensure Fake Copy
        # A resolve represents a resolution to a dispute,
        # releasing the associated held funds.
        # Funds that were previously disputed are no longer disputed.
        # Like dispute s, resolve s do not specify an amount.
        # Instead they refer to a transaction that was under dispute by ID.

        self.debug_print('#######################################')
        self.debug_print('Before Resolve-> ' + str(client_dict))

        x = transaction_dict['tx']
        transaction = self.find_transcaction(x)
        if transaction != False:
            if self.isTXUnderDispute(x) == True:
                # This means that the clients held funds should decrease by the amount no longer disputed,
                # their available funds should increase by the amount no longer disputed,
                # and their total funds should remain the same.
                self.debug_print('Transaction = ' + str(transaction))

                past_amount = transaction['amount']
                self.debug_print('Past Amount = ' + str(past_amount))

                self.debug_print('Held - ' + str(past_amount))
                client_dict['held'] -= past_amount

                self.debug_print('Available + ' + str(past_amount))
                client_dict['available'] += past_amount

                self.check_data(client_dict['available'], client_dict['held'], client_dict['total'])
                if self.negatives_in_data(client_dict['available'], client_dict['held'], client_dict['total']) == False:
                    self.client_accounts_dict[transaction_dict['client']] = client_dict
                    self.debug_print('After Resolve-> ' + str(client_dict))
                    self.resolved_transactions.append(transaction_dict['tx'])
                else:
                    self.debug_print("Negative Number Found! " + str(client_dict['available']) + ',' + str(client_dict['held']) + ',' + str(client_dict['total']) + " Skipping Transaction")
                    self.debug_print('After  Resolve-> ' + str(self.client_accounts_dict[transaction_dict['client']]))

            else:
                #if the tx isn't under dispute
                # you can ignore the resolve and assume this is an error on our partner's side.
                self.debug_print('Transaction -> ' + str(x) + ' Is Not Under Dispute! Skipping Transaction.')
                self.debug_print('After  Resolve-> ' + str(client_dict))


        else:
            # If the tx specified doesn't exist,
            # you can ignore the resolve and assume this is an error on our partner's side.
            self.debug_print('Transaction -> ' + str(x) + ' Doesnt Exist! Skipping Transaction.')
            self.debug_print('After  Resolve-> ' + str(client_dict))


    def chargeback(self, transaction_dict, client_dict):
        client_dict = copy.copy(client_dict) #Ensure Fake Copy
        # A chargeback is the final state of a dispute and represents the client reversing a transaction.
        # Funds that were held have now been withdrawn.
        # Like a dispute and a resolve a chargeback refers to the transaction by ID ( tx ) and does not specify an amount.


        self.debug_print('#######################################')
        self.debug_print('Before Chargeback-> ' + str(client_dict))

        x = transaction_dict['tx']
        transaction = self.find_transcaction(x)
        if transaction != False:
            if self.isTXUnderDispute(x) == True:
                # This means that the clients held funds and total funds should decrease by the amount #previously disputed.
                # If a chargeback occurs the client's account should be immediately frozen.
                self.debug_print('Transaction = ' + str(transaction))

                past_amount = transaction['amount']
                self.debug_print('Past Amount = ' + str(past_amount))

                self.debug_print('Held - ' + str(past_amount))
                client_dict['held'] -= past_amount

                self.debug_print('Total - ' + str(past_amount))
                client_dict['total'] -= past_amount

                self.debug_print('Locked Account = ' + 'True')
                client_dict['locked'] = True

                self.check_data(client_dict['available'], client_dict['held'], client_dict['total'])
                if self.negatives_in_data(client_dict['available'], client_dict['held'], client_dict['total']) == False:
                    self.client_accounts_dict[transaction_dict['client']] = client_dict
                    self.debug_print('After Chargeback-> ' + str(client_dict))
                else:
                    self.debug_print("Negative Number Found! " + str(client_dict['available']) + ',' + str(client_dict['held']) + ',' + str(client_dict['total']) + " Skipping Transaction")
                    self.debug_print('After Chargeback-> ' + str(client_dict))

            else:
                # if the tx isn't under dispute
                # you can ignore the resolve and assume this is an error on our partner's side.
                self.debug_print('Transaction -> ' + str(x) + ' Is Not Under Dispute! Skipping Transaction.')
                self.debug_print('After  Resolve-> ' + str(client_dict))

        else:
            # if the tx specified doesn't exist,
            # you can ignore chargeback and assume this is an error on our partner's side.
            self.debug_print('Transaction -> ' + str(x) + ' Doesnt Exist! Skipping Transaction.')
            self.debug_print('After Chargeback-> ' + str(client_dict))

    def write_accounts_out(self):
        csv_columns = ['client', 'available', 'held', 'total', 'locked']
        self.writer = csv.DictWriter(sys.stdout, fieldnames=csv_columns, lineterminator='\n')
        self.writer.writeheader()
        for client_id in self.client_accounts_dict:
            dict = self.client_accounts_dict[client_id]
            dict['available'] = self.truncate_float(dict['available'])
            dict['held'] = self.truncate_float(dict['held'])
            dict['total'] = self.truncate_float(dict['total'])
            self.writer.writerow(dict)

    def create_new_client(self,transaction_dict):
        client_dict = {}
        client_dict['client'] = int(transaction_dict['client'])
        client_dict['available'] = 0
        client_dict['held'] = 0
        client_dict['total'] = 0
        client_dict['locked'] = False
        self.client_accounts_dict[transaction_dict['client']] = client_dict
        return client_dict


    def test_type(self,type):
        # type string A string corresponding to one of: {"deposit", "withdrawal", "dispute", "resolve", "chargeback"}
        if type not in ['deposit','withdrawal','dispute','resolve','chargeback']:
            raise Exception('Unknown Type!')

    def test_client(self,client):
        # client u16 is a valid u16 client ID
        if client > u16:
            raise Exception('Client ID IS Too Large')
        elif client < 0:
            raise Exception('Client ID IS Too Small')

    def test_tx(self,tx):
        # tx u32 is a valid u32 transaction ID
        if tx > u32:
            raise Exception('TX# Is Too Large')
        elif tx < 0:
            raise Exception('TX# Is Too Small')

    def test_amount(self,amount):
        # amount decimal Decimal value with a precision of up to four places past the decimal
        # You can assume a precision of four places past the decimal and should output values with the same level of precision.
        if amount < 0:
            raise Exception('({}) Amount Is Too Small'.format(str(amount)))

    def run(self):
        self.transactions_list = []
        self.all_account_id_numbers = []
        self.client_accounts_dict = {}
        self.resolved_transactions = []


        with open(self.transactions_csv, 'r') as transactions_csv:
            csv_reader = csv.reader(transactions_csv)
            # Skip Labels
            next(csv_reader)
            for transaction in csv_reader:
                transaction_dict = {}

                transaction_dict['type'] = str(transaction[0])
                self.test_type(transaction_dict['type'])

                transaction_dict['client'] = int(transaction[1])
                self.test_client(transaction_dict['client'])

                transaction_dict['tx'] = int(transaction[2])
                self.test_tx(transaction_dict['tx'])

                if transaction[3] == '':
                    transaction[3] = 0
                transaction_dict['amount'] = self.truncate_float(transaction[3])

                self.test_amount(transaction_dict['amount'])

                if transaction_dict['client'] in self.client_accounts_dict:
                    client_dict = self.client_accounts_dict[transaction_dict['client']]
                else:
                    # There are multiple clients. Transactions reference clients. If a client doesn't exist create a new record;
                    client_dict = self.create_new_client(transaction_dict)

                if transaction_dict['type'] == 'deposit':
                    self.deposit(transaction_dict,client_dict)

                elif transaction_dict['type'] == 'withdrawal':
                    self.withdrawal(transaction_dict, client_dict)

                elif transaction_dict['type'] == 'dispute':
                    self.dispute(transaction_dict, client_dict)

                elif transaction_dict['type'] == 'resolve':
                    self.resolve(transaction_dict, client_dict)

                elif transaction_dict['type'] == 'chargeback':
                    self.chargeback(transaction_dict, client_dict)
                else:
                    raise Exception('Uknkown Type!')

        self.write_accounts_out()


#####################
if __name__ == "__main__":
    Bool = isDebug()
    #Bool = True
    #for test in os.listdir('tests{}'.format(os.sep)):
    #    print('#test = "{}"'.format(test))
    #test = "chargeback_fail_resolved.csv"#PASS
    #test = "chargeback_fail_no_dispute.csv"#PASS
    #test = "chargeback_fail_no_tx.csv"#PASS
    #test = "chargeback_simple.csv"#PASS
    #test = "deposit_fail_negative.csv"#PASS
    #test = "deposit_simple.csv"#PASS
    #test = "dispute_fail_no_tx.csv"#PASS
    #test = "dispute_simple.csv"#PASS
    #test = "mixed_accounts.csv"#PASS
    #test = "Reject_Negative_Transactions.csv"#PASS
    #test = "resolve_fail_no_dispute.csv"#PASS
    #test = "resolve_fail_no_tx.csv"#PASS
    #test = "resolve_simple.csv"#PASS
    #test = "withdrawal_fail_negative_balance.csv"#PASS
    #test = "withdrawal_fail_negative_number.csv"#PASS
    #test = "withdrawal_simple.csv"#PASS
    try:
        transactions_csv = sys.argv[1]
    except IndexError:
        transactions_csv = "transactions.csv"
        #transactions_csv = 'tests{}{}'.format(os.sep,test)
    Payment_Engine = Payment_Engine_Class(transactions_csv,isDebug=Bool)
    Payment_Engine.run()

