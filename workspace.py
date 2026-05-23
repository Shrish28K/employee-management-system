from tabulate import tabulate
from datetime import datetime


class Employee:
    def __init__(self, conn, cur):
        self.conn = conn
        self.cur = cur
        self.log_data=Log(self.conn, self.cur)

    def employeeExist(self, empid):
        #checks the existence of employee in the employee table
        self.cur.execute("""
            SELECT emp_id
            FROM employee
            WHERE emp_id = ?
        """, (empid,))
        result = self.cur.fetchone()
        if result:
            print("Employee already exists")
            self.log_data.log("Searched if empid:{} exists".format(empid))
            return False
        else:
            return True

    def AddEmployee(self):
        #adds employee in the employee table
        try:
            empid = int(input("Enter Employee ID: "))
        except ValueError:
            print("Please enter a valid Employee ID")
            return
        if self.employeeExist(empid):
            name = input("Enter Employee name: ")
            try:
                age = int(input("Enter Employee Age: "))
            except ValueError:
                print("Enter valid age")
                return

            department = input("Enter Employee Department: ")
            job = input("Enter Employee Job: ")
            try:
                salary = int(input("Enter Employee Salary: "))
            except ValueError:
                print("Enter valid salary")
                return
            self.cur.execute("""
                INSERT INTO employee(
                emp_id,
                name,
                age,
                department,
                job,
                salary
                )VALUES(?,?,?,?,?,?)
            """,(empid,name,age,department,job,salary))
            self.conn.commit()
            self.log_data.log(f"Employee emp_id:{empid}, name:{name} was added")
            print("Employee Added successfully")
            self.EmployeeDetails(empid)

    def EmployeeDetails(self, empid=None):
        #if no argument entered for empid then,
        #it prints data of selected empid
        if empid == None:
            try:
                empid = int(input("Enter Employee ID: "))
            except ValueError:
                print("Please enter a valid Employee ID")
                return self.EmployeeDetails(None)
        self.cur.execute("""SELECT * FROM employee WHERE emp_id = ?
        """, (empid,))
        table = self.cur.fetchall()
        if not table:
            print("Employee does not exist")
            return

        headers = ['Employee ID','Name','Age','Department','Job','Salary']
        print(tabulate(table,headers=headers,tablefmt='psql'))

    def AllEmployeeDetails(self):
        #prints all employee data
        self.cur.execute("""SELECT * FROM employee""")
        table = self.cur.fetchall()
        if not table:
            print("No employee records found")
            return
        headers = ['Employee ID','Name','Age','Department','Job','Salary']
        print(tabulate(table,headers=headers,tablefmt='psql'))

    def DeleteEmployeeDetails(self):
        #deletes specific employee details
        print("Delete Employee Details")
        try:
            empid = int(input("Enter Employee ID: "))
        except ValueError:
            print("Please enter a valid Employee ID")
            return self.DeleteEmployeeDetails()
        self.cur.execute("""DELETE FROM employee WHERE emp_id = ?""",(empid,))
        self.conn.commit()
        self.log_data.log(f"Employee with emp_id:{empid} was deleted")
        print("Employee deleted successfully")


    def DeleteAllEmployeeDetails(self):
        #deletes all employee data
        ask=input("Are you sure you want to delete all employee details? (y/n)")
        if ask.lower() == "y":
            self.cur.execute("""DELETE FROM employee""")
            self.conn.commit()
            self.log_data.log(f"All Employee deleted")
            print("All Employee record deleted")
        elif ask.lower() == "n":
            pass
        else:
            self.DeleteEmployeeDetails()
    def DeleteByFilter(self):
        #deletes data from employee based on certain conditions(filters)
        filterData = Filter(self.conn, self.cur)
        result = filterData.filter(printTable=False)
        if result is None:
            return
        ops, val = result
        query = f"DELETE FROM employee WHERE {ops} ?"
        self.cur.execute(query, (val,))
        self.conn.commit()
        self.log_data.log(f"Employee with {ops}{val} deleted")
        print("Records deleted successfully")

    def UpdateEmployeeDetails(self):
        print("Update Employee Details")
        try:
            empid = int(input("Enter Employee ID: "))
        except ValueError:
            print("Please enter a valid Employee ID")
            return self.UpdateEmployeeDetails()
        self.cur.execute("""
                         SELECT *
                         FROM employee
                         WHERE emp_id = ?
                         """, (empid,))
        if not self.cur.fetchone():
            print("Employee does not exist")
            return
        allowed_columns = ["name","age","department","job","salary"]
        column = input("Enter field to update(Name,Age,Department,Job,Salary): ").lower()
        value=input("Enter value: ")
        if column not in allowed_columns:
            print("Invalid field")
            return

        numeric_columns = ["age", "salary"]
        if column in numeric_columns:
            try:
                new_value = int(value)
            except ValueError:
                print("Please enter Integer value only")
                return
        else:
            new_value = value
        query = f"""UPDATE employee SET {column} = ? WHERE emp_id = ?"""
        self.cur.execute(query, (new_value, empid))
        self.conn.commit()
        self.log_data.log(f"Employee emp_id:{empid} updated {column} to {new_value}")
        print("Employee updated successfully")
        self.EmployeeDetails(empid)


class Filter:
    def __init__(self, conn, cur):
        self.conn = conn
        self.cur = cur

    def filter(self,printTable=True):
        #filters and prints data based on conditions
        allowed_columns = ["emp_id","name","age","department","job","salary"]
        allowed_operations = ["=",">","<",">=","<=","!="]

        print("Available Columns:emp_id, name, age, department, job, salary")
        what=input("Enter What you want to filter: ").lower()
        numeric_column=['salary','emp_id',"age"]

        if what not in allowed_columns:
            print("Invalid column name")
            return self.filter(printTable)

        if what in numeric_column:
            try:
                operation=input("Enter the Operation (Eg : =,>,<, >=,<=,!=):")
                if operation not in allowed_operations:
                    print("Invalid operation")
                    return self.filter(printTable)
                values=int(input("Enter Values: "))
            except ValueError:
                print("Please enter a valid number")
                return self.filter(printTable)
        else:
            values=input("Enter Values: ")
            operation="="
        query=f"""
               SELECT * FROM employee
               WHERE {what} {operation} ?
               """
        self.cur.execute(query,(values,))
        table = self.cur.fetchall()

        if not table:
            print("No employee records found")
            return

        if printTable:
            headers = ['Employee ID', 'Name', 'Age', 'Department', 'Job', 'Salary']
            print(tabulate(table, headers=headers, tablefmt='psql'))
        else:
            return f'{what} {operation}',values

class Log:
    def __init__(self, conn, cur):
        self.conn = conn
        self.cur = cur

        cur.execute("""CREATE TABLE IF NOT EXISTS log(
        task TEXT NOT NULL,
        time datetime NOT NULL)""")
        self.conn.commit()
    def log(self,task):
        #stores the data,when was employee table data changed in log table
        time = datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")
        self.cur.execute("""INSERT INTO log(task,time) VALUES (?,?)""",(task,time))
        self.conn.commit()
    def printLog(self):
        self.cur.execute("""SELECT * FROM log""")
        table = self.cur.fetchall()
        if not table:
            print("No employee records found")
            return
        headers = ['Task','Time']
        print(tabulate(table, headers=headers, tablefmt='psql'))