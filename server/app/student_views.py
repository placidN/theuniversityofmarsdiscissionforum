from datetime import datetime
import time

from flask import Flask, request, jsonify, make_response


# Custome dependencies
from app import app, CORS
from app.mailer import send_mail
from app.functions import data_cryptographer, random_gen
from app.db_config import add_record, remove_record, modify_record, extract_records, extract_record_data, extract_record, extract_record_list

cors = CORS(app)

CALLER = "http://127.0.0.1:3000"

@app.route("/enroll/student", methods=["POST"])
def enroll():
    if request.method != 'POST':
        resp = make_response(jsonify({'error':'Request method not allowed'}), 405)
        return resp

    rdata = request.get_json()
    fname = rdata["first_name"]
    lname = rdata["last_name"]
    email = rdata["email"]
    pswd = rdata["pswd"]
    level = rdata["level"]
    
    student_id = '{}{}{}'.format(random_gen(8), fname[0].upper(), lname[0].upper())
    request_object = {
        'student_id': student_id,
        'first_name': fname,
        'last_name': lname,
        'email': email,
        'pswd': data_cryptographer('ec', pswd),
        'level': level,
        'profile_photo': '',
        'verified': 0
    }

    # Enroll student
    enroll_student_request = add_record('students', request_object)

    if not enroll_student_request["status"]:
        if enroll_student_request["error"] == 'Record exists':
            resp = make_response(jsonify({'error': 'Student already enrolled'}), 409)
            return resp

        resp = make_response(jsonify({'error': 'Server error'}), 500)
        return resp

    # Send validation email to student
    enc_student_id = data_cryptographer('ec', student_id)
    verification_link = '{}/validate/student?esi={}'.format(CALLER, enc_student_id)
    __mail_request = send_mail(1, email, {'verification_link':verification_link, 'email':email})

    if not __mail_request['status']:
        resp = make_response(jsonify({'error':'Mail sending failed!'}), 501)
        return resp

    resp = make_response(jsonify({'note':'Enrollment successful'}), 201)
    return resp    

@app.route("/student/validate", methods=["PUT"])
def student_validate():
    if request.method != 'PUT':
        resp = make_response(jsonify({'error':'Request method not allowed'}), 405)
        return resp

    rdata = request.get_json()    
    validate_id = rdata["esi"]

    if not validate_id or validate_id == '':
        resp = make_response(jsonify({'error':'Empty request'}), 400)
        return resp

    student_id = data_cryptographer('dc', validate_id)
    validation_request = modify_record('students', 'student_id', student_id, 'verified', 1)

    if not validation_request["status"]:
        if validation_request["error"] == 'Record exists':
            resp = make_response(jsonify({'error': 'Student already enrolled'}), 409)
            return resp
        
        resp = make_response(jsonify({'error': 'Server error'}), 500)
        return resp
    
    student_data_request = extract_record('students', 'student_id', student_id)

    if not student_data_request["status"]:
        if student_data_request["error"] == 'Record not found':
            resp = make_response(jsonify({'error': 'Student record not found'}), 409)
            return resp

        resp = make_response(jsonify({'error': 'Server error'}), 500)
        return resp

    # Collect student data
    email = student_data_request["object"][3]
    fname = student_data_request["object"][1]
    role  = 'student'
    role_note = 'You are allowed to create groups and accept classes from your lecturers.'
    # Send Welcome email to student
    __mail_request = send_mail(0, email, {'f_name':fname, 'role':role, 'role_note':role_note, 'id':student_id, 'email':email})

    if not __mail_request['status']:
        resp = make_response(jsonify({'error':'Mail sending failed!'}), 501)
        return resp

    resp = make_response(jsonify({'note':'Student verified'}), 200)
    return resp

@app.route("/access/student", methods=["POST"])
def access_student():
    if request.method != 'POST':
        resp = make_response(jsonify({'error':'Request method not allowed'}), 405)
        return resp 

    rdata = request.get_json()
    student_id = rdata["stid"]
    student_pass = rdata["stpswd"]

    student_data_request = extract_record('students', 'student_id', student_id)

    if not student_data_request["status"]:
        if student_data_request["error"] == 'Record not found':
            resp = make_response(jsonify({'error': 'Student record not found'}), 409)
            return resp

        resp = make_response(jsonify({'error': 'Server error'}), 500)
        return resp

    hashed = student_data_request["object"][4]

    if student_pass != data_cryptographer('dc', hashed):
        resp = make_response(jsonify({'error': 'Invalid password'}), 401)
        return resp

    student_object = {
        'student_id': student_id,
        'first_name': student_data_request["object"][1],
        'last_name': student_data_request["object"][2],
        'email': student_data_request["object"][3],
        'level': student_data_request["object"][5],
        'profile_photo': student_data_request["object"][6],
        'verified': student_data_request["object"][7]
    }

    resp = make_response(jsonify({'data':student_object}), 200)
    return resp

