from datetime import datetime
import time

from flask import Flask, request, jsonify, make_response
from flask_cors import CORS

# Custome dependencies
from app import app
from app.mailer import send_mail
from app.functions import data_cryptographer, random_gen
from app.db_config import add_record, remove_record, modify_record, extract_records, extract_record_data, extract_record, extract_record_list

CORS(app)
CALLER = "http://127.0.0.1:3000"


@app.route("/enroll/teacher", methods=["POST"])
def teacher_enroll():
    if request.method != 'POST':
        resp = make_response(jsonify({'error':'Request method not allowed'}), 405)
        return resp

    rdata = request.get_json()
    fname = rdata["first_name"]
    lname = rdata["last_name"]
    email = rdata["email"]
    pswd = rdata["pswd"]
    
    teacher_id = '{}{}{}'.format(fname[0].upper(), lname[0].upper(), random_gen(8))
    request_object = {
        'teacher_id': teacher_id,
        'first_name': fname,
        'last_name': lname,
        'email': email,
        'pswd': data_cryptographer('ec', pswd),
        'profile_photo': '',
        'verified': 0
    }

    # Enroll teacher
    enroll_teacher_request = add_record('teachers', request_object)

    if not enroll_teacher_request["status"]:
        if enroll_teacher_request["error"] == 'Record exists':
            resp = make_response(jsonify({'error': 'teacher already enrolled'}), 409)
            return resp

        resp = make_response(jsonify({'error': 'Server error'}), 500)
        return resp

    # Send validation email to teacher
    enc_teacher_id = data_cryptographer('ec', teacher_id)
    verification_link = '{}/validate/teacher?esi={}'.format(CALLER, enc_teacher_id)
    __mail_request = send_mail(1, email, {'verification_link':verification_link, 'email':email})

    if not __mail_request['status']:
        resp = make_response(jsonify({'error':'Mail sending failed!'}), 501)
        return resp

    resp = make_response(jsonify({'note':'Enrollment successful'}), 201)
    return resp    

@app.route("/teacher/validate", methods=["PUT"])
def teacher_validate():
    if request.method != 'PUT':
        resp = make_response(jsonify({'error':'Request method not allowed'}), 405)
        return resp

    rdata = request.get_json()    
    validate_id = rdata["esi"]

    if not validate_id or validate_id == '':
        resp = make_response(jsonify({'error':'Empty request'}), 400)
        return resp

    teacher_id = data_cryptographer('dc', validate_id)
    validation_request = modify_record('teachers', 'teacher_id', teacher_id, 'verified', 1)

    if not validation_request["status"]:
        if validation_request["error"] == 'Record exists':
            resp = make_response(jsonify({'error': 'teacher already enrolled'}), 409)
            return resp
        
        resp = make_response(jsonify({'error': 'Server error'}), 500)
        return resp
    
    teacher_data_request = extract_record('teachers', 'teacher_id', teacher_id)

    if not teacher_data_request["status"]:
        if teacher_data_request["error"] == 'Record not found':
            resp = make_response(jsonify({'error': 'teacher record not found'}), 409)
            return resp

        resp = make_response(jsonify({'error': 'Server error'}), 500)
        return resp

    # Collect teacher data
    email = teacher_data_request["object"][3]
    fname = teacher_data_request["object"][1]

    role = 'teacher'
    role_note = 'You can create groups and classes for you students.'

    # Send Welcome email to teacher
    __mail_request = send_mail(0, email, {'f_name':fname, 'role':role, 'role_note':role_note, 'id':teacher_id, 'email':email})

    if not __mail_request['status']:
        resp = make_response(jsonify({'error':'Mail sending failed!'}), 501)
        return resp

    resp = make_response(jsonify({'note':'teacher verified'}), 200)
    return resp

@app.route("/access/teacher", methods=["POST"])
def access_teacher():
    if request.method != 'POST':
        resp = make_response(jsonify({'error':'Request method not allowed'}), 405)
        return resp 

    rdata = request.get_json()
    teacher_id = rdata["tid"]
    teacher_pass = rdata["tpswd"]

    teacher_data_request = extract_record('teachers', 'teacher_id', teacher_id)

    if not teacher_data_request["status"]:
        if teacher_data_request["error"] == 'Record not found':
            resp = make_response(jsonify({'error': 'teacher record not found'}), 409)
            return resp

        resp = make_response(jsonify({'error': 'Server error'}), 500)
        return resp

    hashed = teacher_data_request["object"][4]

    if teacher_pass != data_cryptographer('dc', hashed):
        resp = make_response(jsonify({'error': 'Invalid password'}), 401)
        return resp

    teacher_object = {
        'teacher_id': teacher_id,
        'first_name': teacher_data_request["object"][1],
        'last_name': teacher_data_request["object"][2],
        'email': teacher_data_request["object"][3],
        'profile_photo': teacher_data_request["object"][5],
        'verified': teacher_data_request["object"][6]
    }

    resp = make_response(jsonify({'data':teacher_object}), 200)
    return resp

