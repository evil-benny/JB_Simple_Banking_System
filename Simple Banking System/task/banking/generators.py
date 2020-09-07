def system(self):
        system = True
        while system:  # The loop that keeps the system running
            user_input = input('1. Create an account\n'
                               '2. Log into account\n'
                               '0. Exit\n')
            if user_input == '1':   # 1 generate account
                self.gen_account()
            elif user_input == '2':     # 0 login
                card_number = input('\nEnter your card number:\n')
                card_pin = input('Enter your PIN:\n')
                try:
                    self.current_data(card_number)
                except TypeError:
                    print('\nWrong card number or PIN!\n')
                else:
                    if card_number == self.card and self.pin == card_pin:  # use fetch here
                        print('\nYou have successfully logged in!\n')   # 0 successful login
                        login = True
                        while login:    # 0 login actions
                            log_input = input('1. Balance\n'
                                              '2. Log out\n'
                                              '0. Exit\n')
                            if log_input == '1':
                                print(f'\nBalance: {self.balance}\n')  # use fetch here
                            elif log_input == '2':
                                print('\nYou have successfully logged out!\n')
                                login = False
                            elif log_input == '0':
                                print('Bye!')
                                system = False
                                login = False
                    else:
                        print('\nWrong card number or PIN!\n')
            elif user_input == '0':
                print('\nBye!')
                system = False
