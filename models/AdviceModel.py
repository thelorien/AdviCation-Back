import smtplib
from decouple import config
from flask import jsonify
from database.db import get_connection
from .entities.Advice import AdviceReport, AdviceList
from .entities.User import UserStudent
from werkzeug.security import check_password_hash
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class AdviceModel():

    @classmethod
    def create_advice(self, advice):
        try:
            connection = get_connection()

            with connection.cursor() as cursor:
                cursor.execute(
                    """ INSERT INTO public.advices(
	                    topic, description, id_subject, date, start_time, end_time, id_teacher)
	                    VALUES (%s, %s, %s, %s, %s, %s, %s); """, (advice.topic, advice.description, advice.id_subject, advice.date, advice.start_time, advice.end_time, advice.id_teacher))
                affected_rows = cursor.rowcount
                connection.commit()
                connection.close()
                response = jsonify(
                    status=409, message='Advice not created'), 409
                if affected_rows != None:
                    response = jsonify(
                        status=200, message='Advice created successfully'), 200
                return response
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def get_all_advices(self):
        try:
            connection = get_connection()

            with connection.cursor() as cursor:
                cursor.execute(
                    """ SELECT a.id, a.topic, s.name, a.description, CAST(a.date AS TEXT), CAST(a.start_time AS TEXT), CAST(a.end_time AS TEXT), (u.first_name ||' '||u.last_name)as teacher
	                    FROM public.advices a
	                    inner join users u on a.id_teacher = u.id 
	                    inner join subjects s on a.id_subject = s.id
                        WHERE CAST((date || ' ' || start_time) AS TIMESTAMP)  >= current_timestamp;
	                    """)
                result = cursor.fetchall()
            advices = []
            for advice in result:
                advices.append(
                    AdviceList(advice[0], advice[1], advice[2], advice[3],
                               advice[4], advice[5], advice[6], advice[7]).to_JSON()
                )
            response = jsonify(
                status=409, message='There are not advices availables'), 409
            if advices != []:
                response = jsonify(
                    status=200, message='list of advices', data=advices), 200
            connection.close()
            return response
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def set_advice(self, advice):
        try:
            connection = get_connection()

            with connection.cursor() as cursor:
                cursor.execute(
                    """SELECT (u.first_name|| ' ' || u.last_name) AS fullname, u.email FROM users u WHERE u.id = %s;""", (advice.id_student,))
                student = cursor.fetchall()

            with connection.cursor() as cursor:
                cursor.execute(
                    """SELECT a.topic FROM advices a WHERE id = %s;""", (advice.id_advice,))
                adviceA = cursor.fetchall()

            with connection.cursor() as cursor:
                cursor.execute(
                    """SELECT (u.first_name|| ' ' || u.last_name) AS fullname, u.email FROM users u 
                        JOIN advices a ON u.id =a.id_teacher 
                        WHERE a.id = %s;""", (advice.id_advice,))
                teacher = cursor.fetchall()

            with connection.cursor() as cursor:
                cursor.execute(
                    """ INSERT INTO public."AdviceSchedule"(
	                    id_advice, id_student, time_advice)
	                    VALUES (%s, %s, %s); """, (advice.id_advice, advice.id_student, advice.time_advice))
                affected_rows = cursor.rowcount
                connection.commit()
                connection.close()
                response = jsonify(
                    status=409, message='Advice not set'), 409
                if affected_rows != None:
                    messageToStudent = MIMEMultipart("alternative")
                    messageToStudent["Subject"] = "Asesoria apartada con exito"
                    messageToStudent["From"] = config('GMAIL_USER')
                    messageToStudent["To"] = student[0][1]
                    html = f"""
                    <html>
                    <body>
                        <p>Hola <i>{student[0][0]}</i>, se ha apartado la asesoria <b>{advice.id_advice}--{adviceA[0][0]}</b> con el profesor <b>{teacher[0][0]}</b> a las <b>{advice.time_advice}</b> con exito.</p>
                    </html>
                    </body>
                    """
                    part1 = MIMEText(html, "html")
                    messageToStudent.attach(part1)

                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    server.login(config('GMAIL_USER'), config('GMAIL_PWSD'))
                    server.sendmail(config('GMAIL_USER'),
                                    student[0][1], messageToStudent.as_string())

                    messageToTeacher = MIMEMultipart("alternative")
                    messageToTeacher["Subject"] = "Asesoria apartada con exito"
                    messageToTeacher["From"] = config('GMAIL_USER')
                    messageToTeacher["To"] = teacher[0][1]
                    html = f"""
                    <html>
                    <body>
                        Hola Profe <i>{teacher[0][0]}</i>, el alumno <b>{student[0][0]}</b> ha apartado la asesoria <b>{advice.id_advice}--{adviceA[0][0]}</b> a las <b>{advice.time_advice}</b> con exito.
                    </html>
                    </body>
                    """
                    part2 = MIMEText(html, "html")
                    messageToTeacher.attach(part2)
                    server.sendmail(config('GMAIL_USER'),
                                    teacher[0][1], messageToTeacher.as_string())
                    server.quit()

                    response = jsonify(
                        status=200, message='Advice setted successfully'), 200
                return response
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def get_advice_schedule(self, id_advice):
        try:
            connection = get_connection()

            with connection.cursor() as cursor:
                cursor.execute(
                    """	SELECT CAST(time_advice AS TEXT) FROM public."AdviceSchedule"
	                    WHERE id_advice = %s;""", (id_advice,))
                resultSchedule = cursor.fetchall()
            timeTaken = []
            for time1 in resultSchedule:
                x = str(time1)
                x = x.replace("(", "")
                x = x.replace(")", "")
                x = x.replace(",", "")
                x = x.replace("'", "")
                timeTaken.append(x)
            with connection.cursor() as cursor2:
                cursor2.execute(
                    """	SELECT CAST(start_time AS TEXT), CAST(end_time AS TEXT) from advices
	                    WHERE id = %s;""", (id_advice,))
                resultAdvice = cursor2.fetchall()
            timeAdvice = []
            for time2 in resultAdvice:
                timeAdvice.append(
                    time2
                )
            hours = AdviceModel.hourInterval(
                timeAdvice[0][0], timeAdvice[0][1], timeTaken)
            if hours == []:
                hours.append("No hay horarios disponibles")
            response = jsonify(
                status=200, message='list of hours', data=hours), 200
            connection.close()
            return response
        except Exception as ex:
            raise Exception(ex)

    def hourInterval(start_time, end_time, timeTaken):
        start_time = start_time.split(":")
        end_time = end_time.split(":")
        start_time = int(start_time[0]) * 60 + int(start_time[1])
        end_time = int(end_time[0]) * 60 + int(end_time[1])
        hours = []
        for i in range(start_time, end_time, 15):
            hour = i // 60
            minutes = i % 60
            if minutes == 0:
                minutes = "00"
            if hour < 10:
                hour = "0" + str(hour)
            completeHour = str(hour) + ":" + str(minutes) + ":00"
            if completeHour not in timeTaken:
                hours.append(completeHour)
        return hours

    @classmethod
    def get_all_advices_teacher(self, id):
        try:
            connection = get_connection()

            with connection.cursor() as cursor:
                cursor.execute(
                    """ SELECT a.id, a.topic, s.name, a.description, CAST(a.date AS TEXT), CAST(a.start_time AS TEXT), CAST(a.end_time AS TEXT), (u.first_name ||' '||u.last_name)as teacher
	                    FROM public.advices a
	                    inner join users u on a.id_teacher = u.id 
	                    inner join subjects s on a.id_subject = s.id
                        WHERE u.id=%s;
	                    """, (id,))
                result = cursor.fetchall()
            advices = []
            for advice in result:
                advices.append(
                    AdviceList(advice[0], advice[1], advice[2], advice[3],
                               advice[4], advice[5], advice[6], advice[7]).to_JSON()
                )
            response = jsonify(
                status=409, message='There are not advices availables'), 409
            if advices != []:
                response = jsonify(
                    status=200, message='list of advices', data=advices), 200
            connection.close()
            return response
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def delete_advice(self, id):
        try:
            connection = get_connection()

            with connection.cursor() as cursor:
                cursor.execute(
                    """SELECT u.email, (u.first_name|| ' ' || u.last_name) AS fullname  FROM users u 
                        JOIN "AdviceSchedule" a ON u.id =a.id_student  
                        WHERE a.id_advice = %s;""", (id,))
                studentEmails = cursor.fetchall()
                if studentEmails != []:
                    for student in studentEmails:
                        server = smtplib.SMTP('smtp.gmail.com', 587)
                        server.starttls()
                        server.login(config('GMAIL_USER'),
                                     config('GMAIL_PWSD'))
                        messageToStudent = MIMEMultipart("alternative")
                        messageToStudent["Subject"] = "Asesoria cancelada"
                        messageToStudent["From"] = config('GMAIL_USER')
                        messageToStudent["To"] = student[0]
                        html = f"""
                        <html>
                        <body>
                            <p>Hola <b>{student[1]}</b>, lamentamos informarte que la asesoria <b>{id}</b> ha sido cancelada por el profesor.</p>
                        </html>
                        </body>
                        """
                        part2 = MIMEText(html, "html")
                        messageToStudent.attach(part2)
                        server.sendmail(config('GMAIL_USER'),
                                        student[0], messageToStudent.as_string())
                        server.quit()

            with connection.cursor() as cursor:
                cursor.execute(
                    """DELETE FROM "AdviceSchedule" a WHERE a.id_advice = %s;""", (id,))
                affected_rows = cursor.rowcount
            connection.commit()

            with connection.cursor() as cursor:
                cursor.execute(
                    """ DELETE FROM public.advices
                        WHERE id=%s;""", (id,))
                affected_rows = cursor.rowcount
            connection.commit()
            connection.close()
            response = jsonify(
                status=409, message='Advice not deleted'), 409
            if affected_rows != None:
                response = jsonify(
                    status=200, message='Advice deleted successfully and emails sent'), 200
            return response
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def addvice_report(self):
        try:
            connection = get_connection()
            with connection.cursor() as cursor:
                cursor.execute(
                    """SELECT a.id, a.topic, s.name, a.description, CAST(a.date AS TEXT), CAST(a.start_time AS TEXT), CAST(a.end_time AS TEXT), (u.first_name ||' '||u.last_name)as teacher
	                    FROM public.advices a
	                    inner join users u on a.id_teacher = u.id 
	                    inner join subjects s on a.id_subject = s.id;""")
                result = cursor.fetchall()
            advices = []
            for advice in result:
                advices.append(
                    AdviceReport(advice[0], advice[1], advice[2], advice[3], advice[4],
                                 advice[5], advice[6], advice[7], 'student').to_JSON()
                )
            for advice in advices:
                with connection.cursor() as cursor2:
                    cursor2.execute(
                        """ SELECT u.id, (u.first_name ||' '||u.last_name) as student, u.email, CAST(a2."date" AS TEXT) AS date_advice, CAST(a.time_advice AS text) AS time_start, CAST(a.time_advice+'00:15:00' AS TEXT) AS end_time
                            FROM public."AdviceSchedule" a
                            INNER JOIN users u on a.id_student = u.id
                            INNER JOIN advices a2 on a.id_advice = a2.id
                            WHERE a.id_advice=%s;""", (advice['id'],))
                    result2 = cursor2.fetchall()
                students = []
                for student in result2:
                    students.append(
                        UserStudent(student[0], student[1],
                                    student[2], student[3], student[4], student[5]).to_JSON()
                    )
                advice['students'] = students
            return advices
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def get_all_advices_student(self, id):
        try:
            connection = get_connection()

            with connection.cursor() as cursor:
                cursor.execute(
                    """ SELECT ad.id, ad.topic, s.name, ad.description, CAST(ad.date AS TEXT), CAST(a.time_advice AS TEXT), CAST(a.time_advice+'00:15:00' AS TEXT), (u.first_name ||' '||u.last_name)as student
	                    FROM public."AdviceSchedule" a
	                    inner join users u on a.id_student  = u.id
	                    inner join advices ad on a.id_advice = ad.id 
	                    inner join subjects s on ad.id_subject = s.id
                        WHERE u.id = %s;
	                    """, (id,))
                result = cursor.fetchall()
            advices = []
            for advice in result:
                advices.append(
                    AdviceList(advice[0], advice[1], advice[2], advice[3],
                               advice[4], advice[5], advice[6], advice[7]).to_JSON()
                )
            response = jsonify(
                status=409, message='There are not advices availables for the student'), 409
            if advices != []:
                response = jsonify(
                    status=200, message='list of advices', data=advices), 200
            connection.close()
            return response
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def delete_advice_student(self, id, id_student, time_advice):
        try:
            connection = get_connection()

            with connection.cursor() as cursor:
                cursor.execute(
                    """ SELECT u.email, (u.first_name|| ' ' || u.last_name) AS fullname 
                        FROM users u
						WHERE id =  %s;""", (id_student,))
                studenData = cursor.fetchall()

            with connection.cursor() as cursor:
                cursor.execute(
                    """SELECT u.email, (u.first_name|| ' ' || u.last_name) AS fullname
                       FROM advices a 
                       INNER JOIN users u on a.id_teacher = u.id
                       WHERE a.id = %s;""", (id,))
                techerData = cursor.fetchall()
                if studenData != []:
                    if techerData != []:
                        server = smtplib.SMTP('smtp.gmail.com', 587)
                        server.starttls()
                        server.login(config('GMAIL_USER'),
                                     config('GMAIL_PWSD'))
                        messageToTeacher = MIMEMultipart("alternative")
                        messageToTeacher["Subject"] = "Asesoria cancelada por estudiante"
                        messageToTeacher["From"] = config('GMAIL_USER')
                        messageToTeacher["To"] = techerData[0][0]
                        html = f"""
                        <html>
                        <body>
                            <p>Hola <b>{techerData[0][1]}</b>, el estudiante {studenData[0][1]} ha eliminado de su calendario la asesoria <b>{id}</b> de las {time_advice} </p>
                        </html>
                        </body>
                        """
                        part2 = MIMEText(html, "html")
                        messageToTeacher.attach(part2)
                        server.sendmail(
                            config('GMAIL_USER'), techerData[0][0], messageToTeacher.as_string())

                        messageToStudent = MIMEMultipart("alternative")
                        messageToStudent["Subject"] = "Asesoria cancelada por usted"
                        messageToStudent["From"] = config('GMAIL_USER')
                        messageToStudent["To"] = studenData[0][0]
                        html = f"""
                        <html>
                        <body>
                            <p>Hola <b>{studenData[0][1]}</b>, has eliminado de tu calendario la asesoria <b>{id}</b> con el profe <b>{techerData[0][0]}</b> de las {time_advice}</p>
                        </html>
                        </body>
                        """
                        part3 = MIMEText(html, "html")
                        messageToStudent.attach(part3)
                        server.sendmail(config('GMAIL_USER'),
                                        studenData[0][0], messageToStudent.as_string())
                        server.quit()

            with connection.cursor() as cursor:
                cursor.execute(
                    """ DELETE FROM "AdviceSchedule" WHERE id_advice = %s AND id_student = %s AND time_advice = %s;""", (id, id_student, time_advice))
                affected_rows = cursor.rowcount
            connection.commit()
            connection.close()
            response = jsonify(
                status=409, message='Advice could\'n be deleted  '), 409
            if affected_rows != None:
                response = jsonify(
                    status=200, message='Advice deleted successfully and emails sent'), 200
            return response
        except Exception as ex:
            raise Exception(ex)
