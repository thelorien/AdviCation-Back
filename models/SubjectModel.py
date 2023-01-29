from multiprocessing import connection
from flask import jsonify
from database.db import get_connection
from .entities.Subject import Subject


class SubjectModel():

    @classmethod
    def get_subjects(self):
        try:
            connection = get_connection()

            with connection.cursor() as cursor:
                cursor.execute(
                    """ SELECT * FROM public.subjects
                        ORDER BY id ASC """)
                result = cursor.fetchall()
            subjects = []
            for subject in result:
                subjects.append(
                    Subject(subject[0], subject[1], subject[2]).to_JSON()
                )
            connection.close()
            return subjects

        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def add_subject(self, name, description):
        try:
            connection = get_connection()

            with connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO public.subjects(name, description) VALUES (%s, %s)""",
                    (name, description))
                affected_rows = cursor.rowcount
                connection.commit()

            connection.close()
            response = jsonify(status=400, message='Failed to add subject'), 400
            if affected_rows==1:
                response = jsonify(status=200, message='Subject added successfully'), 200
            return response
        except Exception as ex:
            raise Exception(ex)

