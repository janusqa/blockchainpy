from copy import deepcopy


persons = [
    {"name": "Max", "age": 29, "hobbies": ["courses", "teaching"]},
    {"name": "Manual", "age": 14, "hobbies": ["bitcoin", "crypto", "basketball"]},
]

names = [person["name"] for person in persons]
print(names)

older_20 = all([person["age"] > 20 for person in persons])
print(older_20)

copied_persons = [person.copy() for person in persons]
copied_persons[0]["name"] = "Maximillian"
print(copied_persons)
print(persons)

p1, p2 = persons
print(p1)
print(p2)
