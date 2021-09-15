import random
import csv
import os
import sys
u16 = 65535
u32 = 4294967295

# transactions_csv = "transactions.csv"
# transactions_csv = "tests{}withdrawal.csv".format(os.sep)

# transactions_csv = "tests{}resolve.csv".format(os.sep)
# transactions_csv = "tests{}lots_of_data.csv".format(os.sep)
# transactions_csv = "tests{}dispute.csv".format(os.sep)
# transactions_csv = "tests{}deposit.csv".format(os.sep)
# transactions_csv = "tests{}chargeback.csv".format(os.sep)

def generate_random_transactions(transactions_csv):
    with open(transactions_csv,'w') as transactions_csv:
        csv_writer = csv.writer(transactions_csv,lineterminator='\n')
        fields = ['type','client','tx','amount']
        csv_writer.writerow(fields)
        past_transactions = [1]
        past_disputes = [1]
        for tx in range(1,20):
            client = random.randint(1, u16)
            type = random.choice(['deposit','withdrawal','dispute','resolve','chargeback'])
            if type not in ['dispute','resolve','chargeback']:
                past_transactions.append(tx)
                amount = round(random.uniform(1,99999.0),4)
            elif type == 'dispute':
                amount = 0
                tx = random.choice(past_transactions)
                past_disputes.append(tx)
            elif type == 'resolve':
                amount = 0
                tx = random.choice(past_disputes)
                #past_disputes.append(tx)
            elif type == 'chargeback':
                amount = 0
                tx = random.choice(past_disputes)
                #past_disputes.append(tx)
            List = [type,client,tx,amount]
           #print('Writing -> ',List)
            csv_writer.writerow(List)

def generate_random_deposit_transactions():
    transactions_csv = "tests{}deposit.csv".format(os.sep)
    with open(transactions_csv,'w') as transactions_csv:
        csv_writer = csv.writer(transactions_csv,lineterminator='\n')
        fields = ['type','client','tx','amount']
        csv_writer.writerow(fields)
        past_transactions = [1]
        past_disputes = [1]
        #for tx in range(2,round(u32/10000000)):
        for tx in range(2,round(u32)):
                client = random.randint(1, u16)
                type = 'deposit'
                past_transactions.append(tx)
                amount = round(random.uniform(1,99999.0),4)
                List = [type,client,tx,amount]
                #print('Writing -> ',List)
                print(List)
                csv_writer.writerow(List)


def generate_random_withdrawl_transactions():
    #transactions_csv = "tests{}withdrawal.csv".format(os.sep)
    transactions_csv = "transactions.csv".format(os.sep)
    with open(transactions_csv,'w') as transactions_csv:
        csv_writer = csv.writer(transactions_csv,lineterminator='\n')
        fields = ['type','client','tx','amount']
        csv_writer.writerow(fields)
        past_transactions = [1]
        past_disputes = [1]
        for tx in range(2,round(u32/10000000)):
            if tx not in past_transactions:
                client = random.randint(1, u16)
                type = 'deposit'
                past_transactions.append(tx)
                amount = round(random.uniform(1,99999.0),4)
                List = [type,client,tx,amount]
               #print('Writing -> ',List)
                #print(List)
                csv_writer.writerow(List)
                tx += 1
                past_transactions.append(tx)
                ################################################
                type = 'withdrawal'
                amount = round(random.uniform(1,amount),4)
                List = [type, client, tx, amount]
                # print('Writing -> ',List)
                #print(List)
                csv_writer.writerow(List)
            else:
                continue


def generate_random_dispute_transactions(transactions_csv):
    with open(transactions_csv,'w') as transactions_csv:
        csv_writer = csv.writer(transactions_csv,lineterminator='\n')
        fields = ['type','client','tx','amount']
        csv_writer.writerow(fields)
        past_transactions = [1]
        past_disputes = [1]
        for tx in range(2,round(u32/10000000)):
            if tx not in past_transactions:
                client = random.randint(1, u16)
                type = 'deposit'
                past_transactions.append(tx)
                amount = round(random.uniform(1,99999.0),4)
                List = [type,client,tx,amount]
               #print('Writing -> ',List)
                #print(List)
                csv_writer.writerow(List)
                tx += 1
                past_transactions.append(tx)
                ################################################
                type = 'withdrawal'
                amount = round(random.uniform(1,amount),4)
                List = [type, client, tx, amount]
                # print('Writing -> ',List)
                #print(List)
                csv_writer.writerow(List)
            else:
                continue



#generate_random_withdrawl_transactions()
generate_random_transactions("transactions.csv")
#generate_random_deposit_transactions()
#generate_random_withdrawl_transactions(transactions_csv)