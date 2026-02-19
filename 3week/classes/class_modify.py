class  Product:
    def __init__(self, name , price):
        self.name = name
        self.price = price

prod = Product("Laptop", 1000)
prod.price = 900
del prod.name

print(prod.price)