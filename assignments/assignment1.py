names = ["David", "Steve", "Adrian"]

for name in names:
    if len(name) > 5:
        print(name)
    if "n" in name or "N" in name:
        print(name)

while len(names) > 0:
    names.pop()

print(names)
