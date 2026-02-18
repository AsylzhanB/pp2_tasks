class Animal:
    def speak(self):
        return "Animal sound"

class Dog(Animal):
    pass

d = Dog()
print(d.speak())