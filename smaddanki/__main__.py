import sys

from .create_username import generate_username


username = generate_username(sys.argv[1], sys.argv[2])


print(username)
