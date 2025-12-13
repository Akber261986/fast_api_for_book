# Python Programming Guide

## Chapter 1: Introduction to Python

Python is a high-level, interpreted programming language known for its simplicity and readability. It was created by Guido van Rossum and first released in 1991.

### Why Python?
- Easy to learn and read
- Versatile and powerful
- Large standard library
- Strong community support

## Chapter 2: Basic Syntax

### Variables and Data Types
Python supports various data types:
- **Integers**: `x = 5`
- **Floats**: `y = 5.5`
- **Strings**: `name = "Python"`
- **Booleans**: `is_true = True`

### Control Structures

#### Conditional Statements
```python
if x > 0:
    print("Positive number")
elif x == 0:
    print("Zero")
else:
    print("Negative number")
```

#### Loops
```python
# For loop
for i in range(5):
    print(i)

# While loop
count = 0
while count < 5:
    print(count)
    count += 1
```

## Chapter 3: Functions and Modules

### Defining Functions
```python
def greet(name):
    return f"Hello, {name}!"

result = greet("Alice")
print(result)
```

### Working with Modules
```python
import math
import random

# Using math module
area = math.pi * (5 ** 2)
print(f"Area of circle: {area}")

# Using random module
random_number = random.randint(1, 10)
print(f"Random number: {random_number}")
```

## Chapter 4: Data Structures

### Lists
Lists are ordered, mutable collections:
```python
fruits = ["apple", "banana", "cherry"]
fruits.append("orange")
print(fruits)
```

### Dictionaries
Dictionaries store key-value pairs:
```python
person = {
    "name": "John",
    "age": 30,
    "city": "New York"
}
print(person["name"])
```

## Chapter 5: Object-Oriented Programming

### Classes and Objects
```python
class Dog:
    def __init__(self, name, breed):
        self.name = name
        self.breed = breed

    def bark(self):
        return f"{self.name} says woof!"

my_dog = Dog("Buddy", "Golden Retriever")
print(my_dog.bark())
```

## Chapter 6: File Handling

### Reading Files
```python
with open("example.txt", "r") as file:
    content = file.read()
    print(content)
```

### Writing Files
```python
with open("output.txt", "w") as file:
    file.write("Hello, Python!")
```

## Chapter 7: Exception Handling

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Cannot divide by zero!")
finally:
    print("This will always execute")
```

## Chapter 8: Popular Libraries

### NumPy
NumPy is fundamental for scientific computing in Python:
```python
import numpy as np
array = np.array([1, 2, 3, 4, 5])
print(array.mean())
```

### Pandas
Pandas is essential for data manipulation:
```python
import pandas as pd
df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
print(df.head())
```

## Chapter 9: Web Development

### Flask Framework
```python
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, World!"

if __name__ == '__main__':
    app.run(debug=True)
```

## Chapter 10: Best Practices

- Use meaningful variable names
- Write clear and concise comments
- Follow PEP 8 style guide
- Write unit tests for your code
- Use virtual environments for projects
- Document your code properly

## Conclusion

Python is a versatile language suitable for various applications, from web development to data science and artificial intelligence. Its simplicity and power make it an excellent choice for both beginners and experienced programmers.