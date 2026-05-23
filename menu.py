import os
import sqlite3
import bcrypt

from workspace import Employee, Filter, Log

class Menu:
    def __init__(self):
        os.makedirs("workspaces",exist_ok=True)
        while True:

            operation = {
                1: self.createWorkspace,
                2: self.openWorkspace,
                3: self.deleteWorkspace
            }

            print("--" * 10)
            print("Employee Management System")
            print("--" * 10)
            print("1.Create workspace")
            print("2.Open workspace")
            print("3.Delete workspace")
            print("4.Exit")
            print("--" * 10)

            self.name = ""

            try:
                try:
                    choice = int(input("Enter Your Choice: "))
                except ValueError:
                    print("Please enter a valid Choice")
                    continue
                if choice in operation:
                    operation[choice]()
                elif choice == 4:
                    try:
                        self.conn.close()
                    except:
                        pass
                    break
                else:
                    print("Invalid choice")
            except ValueError:
                print("Invalid choice")
            except Exception as e:
                print("ERROR:{}".format(e))

    def createWorkspace(self):
        self.name = input("Enter Workspace name: ")
        db_path=f'workspaces/{self.name}.db'
        if not (os.path.exists(db_path)):
            try:
                password = input("SetUp password for your workspace: ")
                hashed_password = bcrypt.hashpw(password.encode(),
                                                bcrypt.gensalt())
                self.conn = sqlite3.connect(db_path)
                self.cur = self.conn.cursor()
                self.cur.execute("""
                    CREATE TABLE IF NOT EXISTS auth(
                    password BLOB NOT NULL
                    )
                """)

                self.cur.execute("""
                    INSERT INTO auth(password)
                    VALUES (?)
                """, (hashed_password,))

                self.cur.execute("""
                    CREATE TABLE IF NOT EXISTS employee(
                    emp_id INTEGER NOT NULL PRIMARY KEY,
                    name TEXT NOT NULL,
                    age INTEGER,
                    department TEXT NOT NULL,
                    job TEXT NOT NULL,
                    salary REAL NOT NULL
                    )
                """)

                self.conn.commit()
                print("Workspace created successfully")
            except Exception as e:
                print("Something went wrong")
                print(e)
        else:
            print("Workspace already exists")

    def authenticate(self):
        password = input("Enter workspace password: ")
        self.cur.execute("""SELECT password FROM auth""")
        stored_hash = self.cur.fetchone()[0]
        if bcrypt.checkpw(
                password.encode(),
                stored_hash):
            print("Access Granted for Workspace")
            return True
        else:
            print("Wrong Password")
            return False

    def openWorkspace(self):
        self.name = input("Enter Workspace name: ")
        db_path=f'workspaces/{self.name}.db'
        if os.path.exists(db_path):
            try:
                self.conn = sqlite3.connect(db_path)
                self.cur = self.conn.cursor()
                log_data = Log(self.conn, self.cur)
                if self.authenticate():
                    employee = Employee(self.conn,self.cur)
                    filter_data = Filter(self.conn,self.cur)
                    while True:
                        operation = {
                            1: employee.EmployeeDetails,
                            2: employee.AllEmployeeDetails,
                            3: employee.AddEmployee,
                            4: employee.DeleteEmployeeDetails,
                            5: filter_data.filter,
                            6: employee.DeleteByFilter,
                            7: employee.UpdateEmployeeDetails,
                            8: log_data.printLog
                        }
                        print("--" * 10)
                        print(f"{self.name}")
                        print("--" * 10)
                        print("1:Show Employee Details")
                        print("2.Show All Employee Details")
                        print("3.Add Employee Details")
                        print("4.Delete Employee Details")
                        print("5.Filter Employee Details")
                        print("6.Delete Employees by Filter")
                        print("7.Update Employee Details")
                        print("8.Show Log data")
                        print("9.Exit")
                        print("--" * 10)
                        try:
                            choice = int(input("Enter Your Choice: "))
                        except ValueError:
                            print("Please enter a valid Choice")
                            continue
                        if choice in operation:
                            operation[choice]()
                        elif choice == 9:
                            self.conn.close()
                            break
                        else:
                            print("Invalid choice")
            except Exception as e:
                print("Something went wrong\nERROR:{}".format(e))
        else:
            print("Workspace does not exist")

    def deleteWorkspace(self):
        print("--" * 10)
        print("Delete Workspace")
        self.name = input("Enter Workspace name: ")
        ask = input("Are you sure you want to delete this Workspace? (y/n) :")
        db_path=f'workspaces/{self.name}.db'
        if os.path.exists(db_path):
            self.conn = sqlite3.connect(db_path)
            self.cur = self.conn.cursor()
            if ask.lower() == "y" and self.authenticate():
                self.conn.close()
                os.remove(db_path)
                print("Workspace deleted","--" * 10,sep="\n")
            elif ask.lower() == "n":
                pass
            else:
                print("Wrong password")
        else:
            print("Workspace does not exist")
if __name__ == "__main__":
    Menu()