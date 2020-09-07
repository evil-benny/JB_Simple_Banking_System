import random
import sqlite3
import math


class BenBank:

    def __init__(self):
        self.is_running = True
        self.card = ''          # 16 digit
        self.mmi = '4'          # 1  digit
        self.bin = '400000'     # 6  digit
        self.ac_id = ''         # 9  digit
        self.checksum = ''      # 1  digit
        self.pin = ''           # 4  digit
        self.balance = 0        # 0  by default
        self.conn = sqlite3.connect('card.s3db')
        self.cur = self.conn.cursor()
        self.lambda_gen = (lambda x: ''.join([str(random.randint(0, 9)) for _ in range(x)]))

    def insert_into_db(self, account_id, card, pin):  # inserts the generated account into the database
        with self.conn:
            self.cur.execute("INSERT INTO card (id, number, pin) VALUES (:id, :number, :pin)", {'id': account_id, 'number': card, 'pin': pin})

    def get_account_by_card_number(self, card):
        self.cur.execute("SELECT * FROM card WHERE number=:number", {'number': card})
        return self.cur.fetchone()

    def gen_checksum_luhn(self):  # return a checksum using the luhn algorithm
        temp_number_list = [n for n in ('400000' + self.ac_id)]                         # original list
        multiply_list = []                                                              # multiply by 2 if every uneven number
        count = 1
        for n in temp_number_list:
            if count % 2 != 0:
                multiply_list.append(str(int(n) * 2))
            else:
                multiply_list.append(n)
            count += 1
        multiply_list = [str(int(n) - 9) if int(n) > 9 else n for n in multiply_list]   # subtract 9 if the number is over 9
        total = sum([int(n) for n in multiply_list])                                    # add up all the numbers
        self.checksum = str((math.ceil(total / 10) * 10) - total)                       # calculate the checksum by subtracting the sum from the next multiple of 10

    def check_checksum_luhn(self, card_number):                                         # return a checksum using the luhn algorithm
        original_number = card_number                                                   # original list
        drop_digit = card_number[:-1]
        multiply_list = []                                                              # multiply by 2 if every uneven number
        count = 1
        for n in drop_digit:
            if count % 2 != 0:
                multiply_list.append(str(int(n) * 2))
            else:
                multiply_list.append(n)
            count += 1
        multiply_list = [str(int(n) - 9) if int(n) > 9 else n for n in multiply_list]   # subtract 9 if the number is over 9
        total = sum([int(n) for n in multiply_list])                                    # add up all the numbers
        checksum = (math.ceil(total / 10) * 10) - total
        print(checksum, original_number[-1])  # calculate the checksum by subtracting the sum from the next multiple of 10
        if checksum != int(original_number[-1]):
            return True
        return False

    def gen_account(self):                                      # generates the account
        self.ac_id = self.lambda_gen(9)                              # generates account ID
        self.gen_checksum_luhn()                                # generates checksum using luhn algorithm based of of bin and account ID
        self.card = self.bin + self.ac_id + self.checksum       # generates the card number
        self.pin = str(self.lambda_gen(4))                           # generates the pin for that account
        self.insert_into_db(int(self.ac_id), str(self.card), str(self.pin))         # Adds the new account to the database

    def current_data(self, card_number):
        self.ac_id, self.card, self.pin, self.balance = self.get_account_by_card_number(card_number)

    def generate_account(self):
        self.gen_account()
        print(f'\n'
              f'Your card has been created\n'
              f'Your card number:\n'
              f'{self.card}\n'  # pull from DB
              f'Your card PIN:\n'
              f'{self.pin}'     # pull from DB
              f'\n')

    def login_actions(self):
        while True:    # 0 login actions
            log_input = input('1. Balance\n'
                              '2. Add income\n'
                              '3. Do transfer\n'
                              '4. Close account\n'
                              '5. Log out\n'
                              '0. Exit\n')
            if log_input == '1':
                self.current_data(self.card)
                print(f'\nBalance: {self.balance}\n')

            elif log_input == '2':
                income = int(input('\nEnter income:\n'))
                with self.conn:
                    self.cur.execute("UPDATE card SET balance = balance + :income WHERE number = :card", {'income': income, 'card': self.card})
                print('Income was added!\n')

            elif log_input == '3':
                transfer_to = input('\nTransfer\n'
                                    'Enter card number:\n')
                self.cur.execute("SELECT number FROM card")
                transfer_account = list(zip(*self.cur.fetchall()))

                if self.check_checksum_luhn(transfer_to):
                    print('Probably you made a mistake in the card number. Please try again!\n')
                    # check if the card exists

                elif transfer_to not in transfer_account[0]:
                    print('Such a card does not exist.\n')
                    # check if the users enters his card

                elif self.card == transfer_to:
                    print("You can't transfer money to the same account!\n")

                else:
                    transfer_money = int(input('Enter how much money you want to transfer:\n'))
                    self.current_data(self.card)
                    if transfer_money > self.balance:
                        print('Not enough money!\n')
                        # if not enough money print "Not enough money"

                    else:
                        with self.conn:
                            self.cur.execute("UPDATE card SET balance = balance - :income WHERE number = :card", {'income': transfer_money, 'card': self.card})
                            self.cur.execute("UPDATE card SET balance = balance + :income WHERE number = :card", {'income': transfer_money, 'card': transfer_to})
                        print('Success!\n')
                        # subtracts from the current account and adds the amount to the specified account

            elif log_input == '4':
                with self.conn:
                    self.cur.execute('DELETE FROM card WHERE number = :number', {'number': self.card})
                print('\nYour account has been closed!\n')
                return False

            elif log_input == '5':
                print('\nYou have successfully logged out!\n')
                break

            elif log_input == '0':
                print('\nBye!')
                self.is_running = False
                break
            else:
                print()
                continue

    def login(self):
        card_number = input('\nEnter your card number:\n')
        card_pin = input('Enter your PIN:\n')

        try:
            self.current_data(card_number)

        except TypeError:
            print('\nWrong card number or PIN!\n')

        else:
            if card_number == self.card and self.pin == card_pin:  # use fetch here
                print('\nYou have successfully logged in!\n')   # 0 successful login
                self.login_actions()

            else:
                print('\nWrong card number or PIN!\n')

    def system(self):
        while self.is_running:  # The loop that keeps the system running
            user_input = input('1. Create an account\n'
                               '2. Log into account\n'
                               '0. Exit\n')

            if user_input == '1':
                self.generate_account()

            elif user_input == '2':
                self.login()

            elif user_input == '0':
                print('\nBye!')
                self.is_running = False
                break


BenBank().system()
