from database import connect_to_database
import hashlib
import random
import time
import string

# Encryption And Verify Pin

def hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()

def verify_pin(input_pin,stored_pin):
    return hash_pin(input_pin) == stored_pin

# DB And Table Initialize
def initalize_tables():

    connection=connect_to_database()

    if not connection:
        return False
    
    try:
        cursor=connection.cursor()
        create_accounts_table="""
            CREATE TABLE IF NOT EXISTS accounts(
            account_number VARCHAR(50) PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            pin VARCHAR(64) NOT NULL,
            balance DECIMAL(15,2) DEFAULT 0.00,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """

        create_audit_table="""
            CREATE TABLE IF NOT EXISTS audit_table(
            id SERIAL PRIMARY KEY,
            account_number VARCHAR(50),
            holder_name VARCHAR(100),
            action VARCHAR(100) NOT NULL,
            amount DECIMAL(15,2) DEFAULT 0.00,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_number) REFERENCES accounts(account_number) ON DELETE CASCADE ON UPDATE CASCADE
            );
        """

        cursor.execute(create_accounts_table)
        cursor.execute(create_audit_table)
  
        connection.commit()
        cursor.close()
        return True


    except Exception as error:
        print(f"Error intializing tables : {error}")
        return False
    

class Account:
    def __init__(self,name="",pin="",account_number=""):

        self.__account_number=(
            account_number if account_number else self.__generate_account_number()
        )
        self.__name=name
        self.__pin=hash_pin(pin) if pin else ""
        self.__balance=0.0

    def __generate_account_number(self):
        return "".join(random.choices(string.ascii_uppercase+string.digits,k=10))
    

    #GETTERS
    def get_account_number(self):
        return self.__account_number
    
    def get_name(self):
        return self.__name
    
    def get_pin_hash(self):
        return self.__pin
    
    def get_balance(self):
        return self.__balance
    

    #SETTERE
    def set_name(self,name):
        self.__name=name
    
    def set_pin(self,pin):
         self.__pin=hash_pin(pin)
    
    def set_balance(self,balance):
         self.__balance=balance


    #Utility
    def deposite(self,amount):
        if amount <= 0:
            return False
        self.__balance += amount
        return True
    
    def withdraw(self,amount):
        if amount <= 0 or amount > self.__balance:
            return False
        self.__balance -= amount
        return True
    

    #Database CRUD
    @classmethod
    def load_from_db(cls,account_number,pin):
        connection = connect_to_database()

        if not connection:
            return False
        
        try:
            cursor=connection.cursor()
            cursor.execute("SELECT account_number,name,pin,balance FROM accounts WHERE account_number=%s",(account_number,),)
            result=cursor.fetchone()
            connection.commit()
            cursor.close()
            
            if result:
                stored_pin_hash=result[2]
                if verify_pin(pin,stored_pin_hash):
                    account=cls(result[1],pin,result[0])
                    account.set_balance(float(result[3]))
                    return account
                

        except Exception as error:
            print(f"Error Loading Account {error}")
            return None


    
    def save_to_db(self):
        connection = connect_to_database()

        if not connection:
            return False
        
        try:
            cursor=connection.cursor()
            cursor.execute("""
                INSERT INTO accounts(account_number,name,pin,balance)
                VALUES (%s,%s,%s,%s)
                ON CONFLICT(account_number)
                DO UPDATE SET name=%s,pin=%s,balance=%s
            """,
            (
                self.__account_number,
                self.__name,
                self.__pin,
                self.__balance,
                self.__name,
                self.__pin,
                self.__balance,
            ))
            connection.commit()
            cursor.close()
            return True
        
        except Exception as error:
            print(f"Error Creating/Updating Account {error}")
            return None


    def delete_to_db(self):
        connection = connect_to_database()

        if not connection:
            return False
        
        try:
            cursor=connection.cursor()
            cursor.execute("DELETE FROM accounts WHERE account_number=%s",(self.__account_number,),)
               
            connection.commit()
            cursor.close()
            return True
        
        except Exception as error:
            print(f"Error Closing Account {error}")
            return None


class Audit:
    @staticmethod
    def log_action(account_number,holder_name,action,amount=0.0):
        connection = connect_to_database()

        if not connection:
            return False
        
        try:
            cursor=connection.cursor()
            cursor.execute("INSERT INTO audit_table(account_number,holder_name,action,amount) VALUES (%s,%s,%s,%s)",
                (
                 account_number,
                 holder_name,
                 action,
                 amount,
                 ),
            )
                
            connection.commit()
            cursor.close()
            return True
        
        except Exception as error:
            print(f"Error auditing action {error}")
            return None


    @staticmethod
    def get_single_audit_log(account_number):
        connection = connect_to_database()

        if not connection:
            return []
        
        try:
            cursor=connection.cursor()
            cursor.execute("""
            SELECT id,holder_name,action,amount,timestamp FROM audit_table
            WHERE account_number=%s
            ORDER BY timestamp DESC """,
            (account_number,),
            )
            
            result=cursor.fetchall()
            connection.commit()
            cursor.close()
            logs=[]
            for row in result:
                logs.append({
                    "id":row[0],
                    "holder_name":row[1],
                    "action":row[2],
                    "amount":row[3],
                    "timestamp":row[4]
                })
            return logs
        
        except Exception as error:
            print(f"Error Logging {account_number} action {error}")
            return None



    @staticmethod
    def get_all_audit_log():
        connection = connect_to_database()

        if not connection:
            return []
        
        try:
            cursor=connection.cursor()
            cursor.execute("""
            SELECT id,holder_name,action,amount,timestamp FROM audit_table
            ORDER BY timestamp DESC """
            )
            
            result=cursor.fetchall()
            connection.commit()
            cursor.close()
            logs=[]
            for row in result:
                logs.append({
                    "id":row[0],
                    "holder_name":row[1],
                    "action":row[2],
                    "amount":row[3],
                    "timestamp":row[4]
                })
            return logs
        
        except Exception as error:
            print(f"Error Logging all action {error}")
            return None



    @staticmethod
    def clear_single_audit_log(account_number):
        connection = connect_to_database()

        if not connection:
            return False
        
        try:
            cursor=connection.cursor()
            cursor.execute("""
            DELETE FROM audit
            WHERE account_number=%s""",
            (account_number,),
            )
            
        
            connection.commit()
            cursor.close()
        
            return True
        
        except Exception as error:
            print(f"Error Clearing {account_number} action {error}")
            return False



    @staticmethod
    def clear_all_audit_log():
        connection = connect_to_database()

        if not connection:
            return False
        
        try:
            cursor=connection.cursor()
            cursor.execute("DELETE FROM audit_table")
            
            
            connection.commit()
            cursor.close()
            
            return True
        
        except Exception as error:
            print(f"Error Clearing all action {error}")
            return False


class BankSystem():
    def __init__(self):
        initalize_tables()

    def create_account(self,name,pin):
        account=Account(name,pin)

        if account.save_to_db():
            Audit.log_action(account.get_account_number(),account.get_name(),"Account Created",0.00)
            return account
        
        return None
    

    def read_account(self,account_number,pin):
        account=Account.load_from_db(account_number,pin)

        if account:
            Audit.log_action(account_number,account.get_name(),"Details Cheked",0.00)
            return account
        
        return None
    

    def update_account(self,account):
        return account.save_to_db()
    
      
      
    def delete_account(self,account_number,pin):
        account=Account.load_from_db(account_number,pin)

        if account:
            success= account.delete_to_db()

            if success:
                Audit.log_action(account_number,account.get_name(),"Account Deleted",0.00)
                return True
        
        return False
    

    def deposite(self,account_number,pin,amount):
        account=Account.load_from_db(account_number,pin)

        if account and account.deposite(amount):
            account.save_to_db()
            Audit.log_action(account_number,account.get_name(),"Amount Deposited",amount)
            return True
        
        return False
    
    
    def withdraw(self,account_number,pin,amount):
        account=Account.load_from_db(account_number,pin)

        if account and account.withdraw(amount):
            account.save_to_db()
            Audit.log_action(account_number,account.get_name(),"Amount Withdraw",amount)
            return True
        
        return False
    

    def get_account_balance(self,account_number,pin):
        account=Account.load_from_db(account_number,pin)

        if account:
            Audit.log_action(account_number,account.get_name(),"Balance Checked",0.00)
            return account.get_balance()
        
        return None
    

    def get_single_audit_logs(self,account_number):
        return Audit.get_single_audit_log(account_number)
    

    def get_all_audit_logs(self):
        return Audit.get_all_audit_log()
    

    def clear_single_audit_logs(self,account_number):
        return Audit.clear_single_audit_log(account_number)
    

    def clear_all_audit_logs(self):
        Audit.clear_all_audit_log()
    

def valid_amount(prompt):
    while True:
        try:
            amount=float(input(prompt))
            if amount <= 0:
                print("Amount must be greater then zero.")
                continue
            return amount
        except ValueError:
            print("Please enter valid amount!")
    
    

#CLI Function

def create_account_cli(bank):
     print("="*40)
     print("Create New Account")
     print("=" * 40)

     name=input("Enter your name : ").strip()
     if not name:
         print("Name can not be empty/ignored.")
         input("Press Enter to continue...")
         return
     
     pin=input("Enter 4 digit pin : ").strip()
     if len(pin)!=4 or not pin.isdigit():
         print("Pin must be 4 digit number only.")
         input("Press Enter to continue...")
         return
     
     confirm_pin=input("Confirm your pin : ").strip()
     if pin != confirm_pin:
         print("Pin Not matching...")
         input("Press Enter to continue...")
         return
     
     account=bank.create_account(name,pin)
     if account:
         print(f"/n Account Succesfully Created!")
         print(f" Account Number: {account.get_account_number()}")
         print(f" Save your ACCOUNT NUMBER & PIN Securley.."   )
     else:
         print(f"/n Account Creation Failed, Try Again!!")
     input("Press Enter to continue...")


def check_balance_cli(bank,account,pin):
     print("="*40)
     print("Current Account Balance")
     print("=" * 40)

     
     balance=bank.get_account_balance(account.get_account_number(),pin)
     if balance is not None:
         print(f"Current Balance: {balance:.2f}")
     else:
         print("Error Checking Balance, Try Again")
     input("Press Enter to continue...")


def deposite_money_cli(bank,account,pin):
     print("="*40)
     print("Deposit Money")
     print("=" * 40)

     amount=valid_amount("Enter Deposit Amount : ")
     if bank.deposite(account.get_account_number(),pin,amount):
        print(f"{amount:.2f} succesfully deposited.")
        balance=bank.get_account_balance(account.get_account_number(),pin)
        if balance is not None:
            print(f"New Balance Balance: {balance:.2f}")
     else:
        print("Error depositing Balance, Try Again")
     input("Press Enter to continue...")

def withdraw_money_cli(bank,account,pin):
     print("="*40)
     print("Withdraw Money")
     print("=" * 40)

     amount=valid_amount("Enter Withdraw Amount : ")
     if bank.withdraw(account.get_account_number(),pin,amount):
        print(f"{amount:.2f} succesfully withdrawn.")
        balance=bank.get_account_balance(account.get_account_number(),pin)
        if balance is not None:
            print(f"New Balance Balance: {balance:.2f}")
     else:
        print("Error withdrawing Balance, Try Again")
     input("Press Enter to continue...")


def transaction_history_cli(bank,account):
    print("="*40)
    print("user Transaction History")
    print("=" * 40)

    logs=bank.get_single_audit_logs(account.get_account_number())
    if not logs:
        print("no Transaction Found!")
    else:
        for log in logs:
            print(f"{log['timestamp']} {log['action']} - {log['amount']:.2f} By: {log['holder_name']}")
   
    input("Press Enter to continue...")

def update_account_info_cli(bank,account,pin):
     print("="*40)
     print("Update Account Info")
     print("=" * 40)

     new_name=input("Enter your name : ").strip()
     if new_name:
         account.set_name(new_name)
         if bank.update_account(account):
             Audit.log_action(account.get_account_number(),account.get_name(),"Account Info Updated",0.0)
             print("Name updated sucessfully")
         else:
             print(f"Error Updating Name, Try Again")
         return
     else:
         print("No changes made..")
         input("Press Enter to continue...")

def change_pin_logout_cli(bank,account,pin):
    print("="*40)
    print("Change Account Pin")
    print("=" * 40)

    old_pin=input("Enter Current Pin : ").strip()

    if old_pin!=pin:
        print("Incorrect Pin")
        input("Press Enter to continue...")
        return False
    new_pin=input("Enter 4 digit pin : ").strip()
    if len(new_pin)!=4 or not new_pin.isdigit():
        print("Pin must be 4 digit number only.")
        input("Press Enter to continue...")
        return
     
    confirm_pin=input("Confirm your pin : ").strip()
    if new_pin != confirm_pin:
        print("Pin Not matching...")
        input("Press Enter to continue...")
        return
    
    account.set_pin(new_pin)
    if bank.update_account(account):
             Audit.log_action(account.get_account_number(),account.get_name(),"Pin Updated",0.0)
             print("Pin updated sucessfully. you will be logged out")
             input("Press Enter to continue...")
             return True
    else:
        print(f"Error Updating Pin, Try Again")
        return False

def delete_account_cli(bank,account,pin):
    print("="*40)
    print("Delete Account")
    print("=" * 40)

    confirm=input("Are you sure, you want to deletethis account (yes/no)? ").strip().lower()
    if confirm!="yes":
        print("Account deleteion cancelled..")
        input("Press Enter to continue...")
        return False
    re_pin=input("re-Enter your Pin  : ").strip()
   
    if re_pin != pin:
        print("Pin Not matching. Account not closed.")
        input("Press Enter to continue...")
        return False
    
    if bank.delete_account(account.get_account_number(),pin):
        print("Account Closed succesfully.")
        input("Press Enter to continue...")
        return True

    print(f"Error Closing Account, Try Again")
    input("Press Enter to continue...")

def admin_menu_cli(bank, admin_account):
    while True:
        print("=" * 45)
        print("ADMIN DASHBOARD")
        print(f"Welcome, {admin_account.get_name()}")
        print("=" * 45)
        print("1. View All Audit Logs")
        print("2. View Single Account Audit Logs")
        print("3. Clear All Audit Logs")
        print("4. Clear Single Account Audit Logs")
        print("5. Logout")
        print("=" * 45)

        choice = input("Enter Your Choice (1-5): ").strip()

        if choice == "1":
            logs = bank.get_all_audit_logs()
            if not logs:
                print("No logs found.")
            else:
                for log in logs:
                    print(
                        f"{log['timestamp']} | "
                        f"{log['action']} | "
                        f"{log['amount']} | "
                        f"{log['holder_name']}"
                    )
            input("Press Enter to continue...")

        elif choice == "2":
            acc_no = input("Enter Account Number: ").strip()
            logs = bank.get_single_audit_logs(acc_no)
            if not logs:
                print("No logs found.")
            else:
                for log in logs:
                    print(
                        f"{log['timestamp']} | "
                        f"{log['action']} | "
                        f"{log['amount']} | "
                        f"{log['holder_name']}"
                    )
            input("Press Enter to continue...")

        elif choice == "3":
            confirm = input("Type YES to confirm clearing ALL logs: ").strip()
            if confirm == "YES":
                bank.clear_all_audit_logs()
                print("All audit logs cleared.")
            else:
                print("Operation cancelled.")
            input("Press Enter to continue...")

        elif choice == "4":
            acc_no = input("Enter Account Number: ").strip()
            confirm = input("Type YES to confirm: ").strip()
            if confirm == "YES":
                bank.clear_single_audit_logs(acc_no)
                print("Selected account logs cleared.")
            else:
                print("Operation cancelled.")
            input("Press Enter to continue...")

        elif choice == "5":
            print("Admin logged out.")
            break

        else:
            print("Invalid choice!")
            input("Press Enter to continue...")

def is_admin(account):
    return account.get_name() == "Admin"

def login_account_cli(bank):
     print("="*40)
     print("Login Account")
     print("=" * 40)

     account_number=input("Enter your Account Number : ").strip()
     if not account_number:
         print("Account Number  can not be empty/ignored.")
         input("Press Enter to continue...")
         return
     
     pin=input("Enter 4 digit pin : ").strip()
     account=bank.read_account(account_number,pin)
     if not account:
         print("Wrong credientials..")
        #  input("Press Enter to continue...")
         return
    
     if is_admin(account):
        admin_menu_cli(bank, account)
        return

     while True:
        print("="*40)
        print(f"Welcome, {account.get_name()}!")
        print(f"Account Number, {account.get_account_number()}!")
        print("=" * 40)
        print("1. Check Current Balanace")
        print("2. Deposite Balanace")
        print("3. Withdraw Balance")
        print("4. Transaction History")
        print("5. Update Account Info")
        print("6. Update Account Pin")
        print("7. Close Account")
        print("8. Logout")
        print("=" * 40)

        choice=input("Enter Your Choice (1-7) : ").strip()

        if choice == "1":
            check_balance_cli(bank,account,pin)
        elif choice == "2":
            deposite_money_cli(bank,account,pin)
        elif choice == "3":
            withdraw_money_cli(bank,account,pin)
        elif choice == "4":
            transaction_history_cli(bank,account)
        elif choice == "5":
            update_account_info_cli(bank,account,pin)
        elif choice=="6":
            if change_pin_logout_cli(bank,account,pin):
                break
        elif choice == "7":
            if delete_account_cli(bank,account,pin):
                break
        elif choice == "8":
            break    
        else:
            print("Invalid choice, Try Again!")
            input("Press Enter to continue...")
     input("Press Enter to continue...")


#Main Menu of CLI
def main_menu_cli():
    bank=BankSystem()
    while True:
        print("="*40)
        print("Bank Managment System")
        print("=" * 40)
        print("1. New Account")
        print("2. Login Account")
        
    
        # print("=" * 10,"ADMINS ONLY","=" * 10)
        # print("3. View All Audit Logs")
        # print("4. View Single Audit  Log")
        # print("5. Clear All Audit Logs")
        # print("6. Clear Single Audit Log")
        print("5. Exit")

        print("=" * 40)

        choice=input("Enter Your Choice (1-5) : ").strip()

        if choice == "1":
            create_account_cli(bank)
        elif choice == "2":
            login_account_cli(bank)
        # elif choice == "4":
        #     bank.get_single_audit_logs(bank.get_account_number())
        # elif choice=="3":
        #     bank.get_all_audit_logs()
        # elif choice=="5":
        #     bank.clear_all_audit_logs()
        # elif choice == "6":
        #     bank.clear_single_audit_logs(bank.get_account_number())
        elif choice == "5":
            print("thank You So Much Using Our Services, do visit again.")
            time.sleep(1)
            break    
        else:
            print("Invalid choice, Try Again!")
            input("Press Enter to continue...")




if __name__=="__main__":
    main_menu_cli()