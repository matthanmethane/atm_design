import hashlib
import requests
import json

class CardReader:
    '''
    Temporary class created for Card Reader
    No real function
    '''
    def verify_card(self):
        return True

class CashBin:
    '''
    Temporary class created for Cash Bin
    Only stores the amount of cash in the bin
    '''
    def __init__(self, total_amount):
        self.amount = total_amount

class ATMCtr:
    '''
    This the controller for the ATM.
    '''
    def __init__(self) -> None:
        self.card_reader = CardReader()
        self.cash_bin = CashBin(1000)
        self.card_no = None
        self.token = None
        self.balance = None
        self.account_no = None
    
    def check_card(self): # Should return card number, None elsewise 
        '''
        This function checks the if the card is valid
        '''
        self.card_no = self.card_reader.verify_card()
        return self.card_no
        
    def verify_pin(self, pin: int) -> bool:
        '''
        This function verifies the PIN that the user inputs
        '''
        # Private data like pin should be hashed before external api calls
        # I'll assume that the bank API and this system shares a MD5 hashing scheme 
        pin_hash = hashlib.md5(str(pin).encode())
        # Arbitrary API link for bank
        r = requests.get(f'https://bank.com/verify?card_no={self.card_no}&pin={pin_hash.hexdigest()}')
        if r.status_code != 200: return False
        # Assume a temp token for interacting with bank API is given inside the response
        # This token will be used to retrieve information about the bank account
        self.token = r.text['token']
        return True
    
    def get_account(self):
        '''
        This function retrieves the accounts of the user and save it temporary in the controller.
        This is saved so that UI developers can easily pick them up to display them
        '''
        r = requests.get(f'https://bank.com/getAccounts?token={self.token}')
        if r.status_code != 200: return False
        account_list = r.text['account']
        if not account_list or account_list==[]: return False
        self.account_list = account_list
        return True
    
    def select_account(self, choice):
        '''
        This function saves the account
        '''
        try:
            self.account_no = self.account_list[choice]
            return True
        except: 
            print("Index out of range")
            return False
    
    def verify_action(self,choice):
        if not choice: return False
        return True if -1<=choice<=2 else False
        
        
    def view_balance(self):
        '''
        This function retrieves the balance and saves it in the Ctr for UI developers to pick up. 
        '''
        r = requests.get(f'https://bank.com/viewBalance?token={self.token}')
        is_successful, balance = r.text['is_successful'], r.text['balance']
        if is_successful: 
            self.balance = balance
            return True
        else:
            print("Failed to get balance.")
            return False
        
    
    def deposit(self, amount):
        '''
        This function handles deposit and saves the new blanace for UI developers.
        '''
        r = requests.get(f'https://bank.com/deposit?token={self.token}amount={amount}')
        is_successful, new_balance = r.text['is_successful'], r.text['balance']
        if not is_successful: 
            print("Not enough balance in your account.")
            return False
        self.balance = new_balance
        print(f"New balance: {new_balance}")
        return True
        
    def withdraw(self, amount):
        '''
        This function handles withrawing. 
        It will make sure that the casn bin has enough amount of money that the user wants to withdraw
        New balance is updated in teh Ctr for UI developers 
        '''
        if amount>self.cash_bin.amount: 
            print("Not enough balance in this ATM. Please try in another ATM nearby.")
            return False
        r = requests.get(f'https://bank.com/withdraw?token={self.token}&amount={amount}')
        is_successful, new_balance = r.text['is_successful'], r.text['balance']
        if not is_successful: 
            print("Not enough balance in your account.")
            return False
        self.cash_bin.amount -= amount
        self.balance = new_balance
        print(f"New balance: {new_balance}")
        return True
    
    def terminate(self):
        '''
        This function is executed whenever a trnasaction is complete.
        It resets all user related information.
        '''
        self.card_no = None
        self.token = None
        self.balance = None
        self.account_no = None
        
    def fsm(self):
        '''
        This is where the flow of the ATM happens.
        It will be called every transaction.
        '''
        if not self.check_card(): 
            self.terminate()
            return {'msg': 'Failed to check card'}

        i = 3
        while True:
            if i==0:
                self.terminate()
                return {'msg': 'Reached maximum number of attempts!'}
            pin = int(input()) 
            if self.verify_pin(pin): break
            i -= 1
                
        
        if not self.get_account(): 
            self.terminate()
            return {'msg': 'Failed to retrieve account!'}
        
        choice = int(input())
        if not self.select_account(choice):
            self.terminate()
            return {'msg': 'Invalid choice!'}
        
        
        choice = int(input())
        if not self.verify_action(choice): 
            self.terminate
            return {'msg': 'Invalid choice!'}
        if choice==0:
            print('Viewing balance...')
            self.view_balance()
        elif choice==1:
            print('Loading...')
            amount = int(input('Enter the amount of money: '))
            self.deposit(amount)
        elif choice==2:
            print('Loading...')
            amount = int(input('Enter the amount of money: '))
            self.withdraw(amount)
        
        
        self.terminate()
        return {'msg': 'Terminating!'}
    