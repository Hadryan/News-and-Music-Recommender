from os import walk
import os
f = []
i = 0
for (dirpath, dirnames, filenames) in walk("fileMyrror"):
    for file in filenames:
        if file.startswith('past_'):
            email = file.split("past_", 1)[1]
            print("email1"+email)
            #email = email.strip(".json")
            print(os.path.splitext(email)[0])


            f.append(file)

print(f)