Tested on Windows and Mac

To run:
	“python payment_engine.py transactions.csv > client_accounts.csv”

To run and display debug information type:
	“python payment_engine.py transactions.csv -d”

Summary:
I sacrificed speed for security, readability, and testing. I thought this was the correct way to go, considering we are hypothetically dealing with money.
•If we removed all the debug_print statements, it would speed up the program, but it would make it harder to test. 
•I used python dictionaries for each transaction to make it more readable but again this might cause it to be slower.
•Throughout the program, I am constantly checking the data, which also causes it to be slower.

Testing:
In the root folder, you will find another folder called “tests”. In here, there are many different transaction scenarios: 
	•"chargeback_fail_no_dispute.csv"
	•"chargeback_fail_no_tx.csv"
	•"chargeback_simple.csv"
	•"deposit_fail_negative.csv"
	•"deposit_simple.csv"
	•"dispute_fail_no_tx.csv"
	•"dispute_simple.csv"
	•"mixed_accounts.csv"
	•"Reject_Negative_Transactions.csv"
	•"resolve_fail_no_dispute.csv"
	•"resolve_fail_no_tx.csv"
	•"resolve_simple.csv"
	•"withdrawal_fail_negative_balance.csv"
	•"withdrawal_fail_negative_number.csv"
	•"withdrawal_simple.csv"

I ran these transactions individually with the -d flag on and manually verified that we were handling the situations correctly. If I had more time, I would automate this.

Note:
•If an error occurs that could be considered malicious, I raise an exception and the entire program will stop. I did this so it would force someone to investigate.
•In some scenarios, where a mistake is considered non-malicious, I skip the transaction and move on. For example, if someone tries to resolve a transaction that doesn’t exist, the program will ignore it.
 













