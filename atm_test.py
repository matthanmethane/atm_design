import unittest
from unittest.mock import patch
from atm import ATMCtr as ATM, CardReader

class Tests(unittest.TestCase):
            
    @patch.object(CardReader,'verify_card')
    def test_check_card(self, mock_verify_card):
        '''
        This test case tests few scenarios with checking the card
        '''
        atm = ATM()
        # Card is verified
        mock_verify_card.return_value = 1234
        self.assertEqual(atm.check_card(), 1234)
        # Card is not verified
        mock_verify_card.return_value = None
        self.assertEqual(atm.check_card(), None)
    
    @patch('atm.requests.get')
    def test_verify_pin(self, mock_req):
        '''
        This test case tests few scenarios with verifying the PIN
        '''
        atm = ATM()
        # API returns a valid response
        mock_req.return_value.status_code = 200
        mock_req.return_value['token'] = '12@3/v2'
        self.assertEqual(atm.verify_pin(1234), True)
        # API returns an Invalid Response
        mock_req.return_value.status_code = 401
        self.assertEqual(atm.verify_pin(0000), False)
        
    @patch('atm.requests.get')
    def test_get_account(self, mock_req):
        '''
        This test case tests few scenarios revolving getting the account
        '''
        atm = ATM()
        # There are valid accounts 
        mock_req.return_value.status_code = 200
        mock_req.return_value.text = {'account': ['savings123', 'credits123']}
        self.assertEqual(atm.get_account(), True)
        self.assertEqual(atm.account_list,['savings123', 'credits123'] )
        # There are no accounts
        mock_req.return_value.text = {'account': []}
        self.assertEqual(atm.get_account(), False)
    
    @patch('atm.requests.get')
    def test_view_balance(self, mock_req):
        '''
        This test case tests few scenarios revolving viewing balance
        '''
        atm = ATM()
        atm.token = '12@3/v2'
        # There are no accounts
        mock_req.return_value.text = {'is_successful': False, 'balance': None}
        status = atm.view_balance()
        self.assertEqual(atm.balance, None)
        self.assertEqual(status,False)
        # Successful to retrieve the balance
        mock_req.return_value.status_code = 200
        mock_req.return_value.text = {'is_successful': True, 'balance': 200}
        status = atm.view_balance()
        self.assertEqual(atm.balance, 200)
        self.assertEqual(status,True)
        
    @patch('atm.requests.get')
    def test_deposit(self, mock_req):
        '''
        This test case tests few scnearios revolving depositing the cash
        '''
        atm = ATM()
        atm.token = '12@3/v2'
        # Failed to add the deposit
        mock_req.return_value.text = {'is_successful': False, 'balance': None}
        status = atm.deposit(300)
        self.assertEqual(atm.balance, None)
        self.assertEqual(status,False)
        # Sucessful to add the deposit
        mock_req.return_value.status_code = 200
        mock_req.return_value.text = {'is_successful': True, 'balance': 500}
        status = atm.deposit(300)
        self.assertEqual(atm.balance, 500)
        self.assertEqual(status,True)
    
    @patch('atm.requests.get')
    def test_withdraw(self, mock_req):
        '''
        This test case tests few scenarios revolving withdrawing of cash
        '''
        atm = ATM()
        atm.token = '12@3/v2'
        # Deposit more than what the Cash Bin has
        mock_req.return_value.text = {'is_successful': False, 'balance': None}
        status = atm.withdraw(1500)
        self.assertEqual(atm.balance, None)
        self.assertEqual(atm.cash_bin.amount, 1000)
        self.assertEqual(status,False)
        # Deposit valid amount
        mock_req.return_value.status_code = 200
        mock_req.return_value.text = {'is_successful': True, 'balance': 1000}
        status = atm.withdraw(800)
        self.assertEqual(atm.balance, 1000)
        self.assertEqual(atm.cash_bin.amount, 200)
        self.assertEqual(status,True)
    
    @patch.object(ATM,'check_card')
    def test_terminate_when_card_invalid(self, mock_fn):
        '''
        This test case tests if the FSM terminatse when the card is not valid
        '''
        mock_fn.return_value = False
        atm = ATM()
        self.assertEqual(atm.fsm()['msg'], 'Failed to check card')
    
    @patch.object(ATM,'verify_pin')
    @patch('builtins.input')
    def test_terminate_when_pin_invalid_three_times(self,mock_input, mock_fn):
        '''
        This test cases tests if the FSM terminates when PIN is input wrongly three times
        '''
        mock_input.side_effect = ['0000', '1111', '2222']
        mock_fn.return_value = False
        atm = ATM()
        self.assertEqual(atm.fsm()['msg'], 'Reached maximum number of attempts!')
    
    @patch.object(ATM,'get_account',return_value=True)
    @patch.object(ATM,'select_account',return_value=True)
    @patch.object(ATM,'verify_action',return_value=True)
    @patch.object(ATM,'view_balance',return_value=True)      
    @patch.object(ATM,'verify_pin',return_value=True)
    @patch('builtins.input')
    def test_terminate_successfully(self, mock_input, mockfn1, mockfn2, mockfn3, mockfn4, mockfn5):
        '''
        This test case tests if the ATM comes to the terminating stage when going through all steps successfully
        '''
        mock_input.side_effect = ['0000','0','0']
        atm = ATM()
        atm.account_list = ['1234']
        self.assertEqual(atm.fsm()['msg'], 'Terminating!')
        

if __name__ == "__main__":
    unittest.main(verbosity=2)