from fileinput import filename
from flask import Blueprint, jsonify, request, send_from_directory, current_app, send_file
from os import path, makedirs

from models.SubjectModel import SubjectModel

main = Blueprint('subject_blueprint', __name__)


@main.route('/get-subjects', methods=['GET'])
def get_subjects():
    try:
        return jsonify(status=200, message='Get subjects', data=SubjectModel.get_subjects()), 200
    except Exception as ex:
        return jsonify(status=500, message=str(ex), method='get-subjects'), 500

@main.route('/add-subject', methods=['POST'])
def add_subjects():
    try:
        name = request.json['name']
        description = request.json['description']
        return SubjectModel.add_subject(name, description)
    except Exception as ex:
        return jsonify(status=500, message=str(ex), method='add-subject'), 500
