from flask import Blueprint, jsonify, request

from models.entities.Advice import Advice, AdviceSchedule
from models.AdviceModel import AdviceModel

main = Blueprint('advice_blueprint', __name__)


@main.route('/add-advice', methods=['POST'])
def add_advice():
    try:

        topic = request.json['topic']
        description = request.json['description']
        id_subject = request.json['id_subject']
        date = request.json['date']
        start_time = request.json['start_time']
        end_time = request.json['end_time']
        id_teacher = request.json['id_teacher']
        advice = Advice(topic, description, id_subject, date,
                        start_time, end_time, id_teacher)

        response = AdviceModel.create_advice(advice)

        return response

    except Exception as ex:
        return jsonify(status=500, message=str(ex), method='add-advice'), 500


@main.route('/get-all-advices', methods=['GET'])
def get_all_advices():
    try:
        response = AdviceModel.get_all_advices()

        return response

    except Exception as ex:
        return jsonify(status=500, message=str(ex), method='get-all-advices'), 500


@main.route('/set-advice', methods=['POST'])
def set_advice():
    try:

        id_advice = request.json['id_advice']
        id_student = request.json['id_student']
        time_advice = request.json['time_advice']
        advice = AdviceSchedule(id_advice, id_student, time_advice)

        response = AdviceModel.set_advice(advice)

        return response

    except Exception as ex:
        return jsonify(status=500, message=str(ex), method='set-advice'), 500


@main.route('/get-advice-schedule', methods=['POST'])
def get_advice_schedule():
    try:

        id_advice = request.json['id_advice']

        response = AdviceModel.get_advice_schedule(id_advice)

        return response

    except Exception as ex:
        return jsonify(status=500, message=str(ex), method='get-advice-schedule'), 500


@main.route('/get-all-advices-teacher/<id>', methods=['GET'])
def get_all_advices_teacher(id):
    try:
        response = AdviceModel.get_all_advices_teacher(id)
        return response
    except Exception as ex:
        return jsonify(status=500, message=str(ex), method='get-all-advices-teacher'), 500


@main.route('/delete-advice', methods=['POST'])
def delete_advice():
    try:
        id_advice = request.json['id_advice']
        response = AdviceModel.delete_advice(id_advice)
        return response
    except Exception as ex:
        return jsonify(status=500, message=str(ex), method='delete-advice'), 500


@main.route('/reports', methods=['GET'])
def reports():
    try:
        response = AdviceModel.addvice_report()
        if response is None:
            return jsonify(status=404, message='No hay datos', method='reports'), 404
        else:
            return jsonify(status=200, message='Reporte generado', data=response, method='reports'), 200
    except Exception as ex:
        return jsonify(status=500, message=str(ex), method='reports'), 500


@main.route('/get-all-advices-student/<id>', methods=['GET'])
def get_all_advices_student(id):
    try:
        response = AdviceModel.get_all_advices_student(id)
        return response
    except Exception as ex:
        return jsonify(status=500, message=str(ex), method='get-all-advices-student'), 500


@main.route('/delete-advice-student', methods=['POST'])
def delete_advice_student():
    try:
        id_advice = request.json['id_advice']
        id_student = request.json['id_student']
        time_advice = request.json['time_advice']
        response = AdviceModel.delete_advice_student(
            id_advice, id_student, time_advice)
        return response
    except Exception as ex:
        return jsonify(status=500, message=str(ex), method='delete-advice-student'), 500
