from flask import jsonify
from database.db import get_connection
from .entities.User import userJoin, UserEdit, UserAdmin
from werkzeug.security import check_password_hash


class UserModel():

    @classmethod
    def login_user(self, email, password):
        try:
            connection = get_connection()

            with connection.cursor() as cursor:
                cursor.execute(
                    """SELECT password, id, id_rol,first_name FROM public.users where email = %s """, (email,))
                result = cursor.fetchone()

                response = jsonify(
                    status=401, message='Login failed, credentials incorrect'), 401
                if result != None and check_password_hash(result[0], password):
                    response = jsonify(
                        status=200, message='Login success', id=result[1], rol=result[2], name=result[3]), 200

            connection.close()
            return response
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def register_user(self, user):
        try:
            connection = get_connection()

            with connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO public.users ( id, first_name, last_name, email, password)
                    VALUES (%s, %s, %s, %s, %s)""", (user.id, user.first_name, user.last_name, user.email, user.password))
                affected_rows = cursor.rowcount
                connection.commit()

            connection.close()
            return affected_rows
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def get_all_users(self):
        try:
            connection = get_connection()

            with connection.cursor() as cursor:
                cursor.execute(
                    """ SELECT u.id, (u.first_name|| ' ' || u.last_name) as fullname, u.email,  r.rol_name
	                    FROM public.users u
	                    LEFT JOIN public."Rols" r ON u.id_rol= r.id
						ORDER BY u.id ASC;""")
                result = cursor.fetchall()

            users = []
            for user in result:
                users.append(
                    UserAdmin(user[0], user[1], user[2], user[3]).to_JSON())

            connection.close()
            return users
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def update_user_rol(self, id, id_role):
        try:
            connection = get_connection()
            with connection.cursor() as cursor:
                cursor.execute(
                    """UPDATE public.users SET id_rol = %s  WHERE id= %s""",
                    (id_role, id))
                affected_rows = cursor.rowcount
                connection.commit()
            connection.close()
            return affected_rows
        except Exception as ex:
            raise Exception(ex)
