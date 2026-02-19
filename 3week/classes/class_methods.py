class Employee:
    company  ="BIGroup"

    def __init__(self, name):
        self.name = name

e1 = Employee("Alice")
e2 = Employee("Eric")

print(e1.company)
print(e2.company)

Employee.company = "KazStroi"

print(e1.company)
print(e2.company)