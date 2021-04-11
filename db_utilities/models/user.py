import enum

class User():
    def __init__(self, id, username, fullname, password, userRole):
        self.id = id
        self.username = username
        self.fullname = fullname
        self.password = password
        self.userRole = userRole

class UserRole(enum.Enum):
  admin = "Admin"
  person = "Person"