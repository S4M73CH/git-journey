"""A small, in-memory ATM simulator for learning and demonstrations."""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


MAX_PIN_TRIALS = 3
DAILY_WITHDRAWAL_LIMIT = Decimal("1000.00")
WITHDRAWAL_DENOMINATION = Decimal("20.00")


@dataclass
class Account:
    number: str
    name: str
    pin: str
    balance: Decimal
    locked: bool = False
    withdrawn_today: Decimal = Decimal("0.00")


class ATMSimulator:
    def __init__(self) -> None:
        # Demo accounts only: data is reset whenever the program exits.
        self.accounts = {
            "1001": Account("1001", "Alex Morgan", "1234", Decimal("1500.00")),
            "1002": Account("1002", "Sam Lee", "4321", Decimal("800.00")),
        }

    @staticmethod
    def money(value: Decimal) -> str:
        return f"${value:,.2f}"

    @staticmethod
    def read_amount(prompt: str) -> Decimal | None:
        raw = input(prompt).strip()
        try:
            amount = Decimal(raw)
        except InvalidOperation:
            print("Please enter a valid amount.")
            return None
        if not amount.is_finite() or amount <= 0:
            print("Amount must be greater than zero.")
            return None
        return amount.quantize(Decimal("0.01"))

    def authenticate(self) -> Account | None:
        number = input("Enter account number (or Q to quit): ").strip()
        if number.upper() == "Q":
            return None
        account = self.accounts.get(number)
        if account is None:
            print("Account not found.")
            return None
        if account.locked:
            print("This card is blocked. Please contact your bank.")
            return None

        for trial in range(1, MAX_PIN_TRIALS + 1):
            pin = input("Enter your 4-digit PIN: ").strip()
            if pin == account.pin:
                print(f"Welcome, {account.name}.")
                return account
            remaining = MAX_PIN_TRIALS - trial
            if remaining:
                print(f"Incorrect PIN. {remaining} attempt(s) remaining.")
            else:
                account.locked = True
                print("Incorrect PIN. Your card is now blocked. Please contact your bank.")
        return None

    def withdraw(self, account: Account) -> None:
        amount = self.read_amount("Withdrawal amount: $")
        if amount is None:
            return
        if amount % WITHDRAWAL_DENOMINATION:
            print("This ATM dispenses amounts in $20 increments.")
        elif amount > account.balance:
            print("Insufficient funds.")
        elif account.withdrawn_today + amount > DAILY_WITHDRAWAL_LIMIT:
            available = DAILY_WITHDRAWAL_LIMIT - account.withdrawn_today
            print(f"Daily withdrawal limit exceeded. Remaining today: {self.money(available)}")
        else:
            account.balance -= amount
            account.withdrawn_today += amount
            print(f"Please take your cash. New balance: {self.money(account.balance)}")

    def deposit(self, account: Account) -> None:
        amount = self.read_amount("Deposit amount: $")
        if amount is not None:
            account.balance += amount
            print(f"Deposit accepted. New balance: {self.money(account.balance)}")

    def transfer(self, account: Account) -> None:
        target_number = input("Destination account number: ").strip()
        target = self.accounts.get(target_number)
        if target is None:
            print("Destination account not found.")
            return
        if target is account:
            print("You cannot transfer to the same account.")
            return
        amount = self.read_amount("Transfer amount: $")
        if amount is None:
            return
        if amount > account.balance:
            print("Insufficient funds.")
            return
        account.balance -= amount
        target.balance += amount
        print(f"Transfer complete. New balance: {self.money(account.balance)}")

    def account_menu(self, account: Account) -> bool:
        while True:
            print("\n1. Balance inquiry\n2. Withdraw\n3. Deposit\n4. Transfer\n5. Change PIN\n6. Finish session")
            choice = input("Choose an option: ").strip()
            if choice == "1":
                print(f"Available balance: {self.money(account.balance)}")
            elif choice == "2":
                self.withdraw(account)
            elif choice == "3":
                self.deposit(account)
            elif choice == "4":
                self.transfer(account)
            elif choice == "5":
                new_pin = input("Enter a new 4-digit PIN: ").strip()
                if len(new_pin) == 4 and new_pin.isdigit():
                    account.pin = new_pin
                    print("PIN changed successfully.")
                else:
                    print("PIN must contain exactly 4 digits.")
            elif choice == "6":
                print("Session ended. Please take your card.")
                return True
            else:
                print("Invalid option. Please choose 1–6.")

    def run(self) -> None:
        print("Welcome to the Python ATM Simulator")
        print("Demo accounts: 1001 (PIN 1234), 1002 (PIN 4321)")
        while True:
            account = self.authenticate()
            if account is None:
                answer = input("Start another session? (Y/N): ").strip().upper()
                if answer != "Y":
                    break
                continue
            self.account_menu(account)
        print("Thank you for using the ATM.")


if __name__ == "__main__":
    ATMSimulator().run()
