from vault import encrypt_message

username = input("Enter your username: ")
password = input("Enter your password: ")

encrypted_username = encrypt_message(username)
encrypted_password = encrypt_message(password)

with open("credentials.txt", "ab") as f:
    f.write(encrypted_username + b"
")
    f.write(encrypted_password + b"
")

print("Credentials saved.")
