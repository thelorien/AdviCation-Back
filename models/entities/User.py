class User():

    def __init__(self, id, first_name, last_name,  email, password) -> None:
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password

    def to_JSON(self):
        return {
            'id': self.id,
            'first name': self.first_name,
            'last name': self.last_name,
            'email': self.email,
            'password': self.password
        }


class userJoin():

    def __init__(self, id, first_name, last_name, email, role) -> None:
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.role = role

    def to_JSON(self):
        return {
            'id': self.id,
            'fist name': self.first_name,
            'last name': self.last_name,
            'email': self.email,
            'role': self.role
        }


class UserEdit():

    def __init__(self, id, first_name, last_name, email) -> None:
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email

    def to_JSON(self):
        return {
            'id': self.id,
            'fist name': self.first_name,
            'last name': self.last_name,
            'email': self.email,
        }


class UserAdmin():
    def __init__(self, id, full_name, email, role) -> None:
        self.id = id
        self.full_name = full_name
        self.email = email
        self.role = role

    def to_JSON(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'role': self.role
        }


class UserStudent():
    def __init__(self, id, full_name, email, date_advice, time_start, time_end) -> None:
        self.id = id
        self.full_name = full_name
        self.email = email
        self.date_advice_student = date_advice,
        self.time_start_student = time_start,
        self.time_end_student = time_end

    def to_JSON(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'date_advice_student': self.date_advice_student,
            'time_start_student': self.time_start_student,
            'time_end_student': self.time_end_student
        }
