# Native Python functions
from datetime import datetime
import time

from flask import Flask, request, jsonify, make_response
from flask_cors import CORS

from app import app
from app.mailer import send_mail
from app.functions import data_cryptographer, random_gen
from app.db_config import add_record, remove_record, modify_record, extract_records, extract_record_data, extract_record, extract_record_list

cors = CORS(app)

@app.route("/")
def index():
    return make_response('Welcome to The University of Mars API')

@app.route("/get/all")
def get_all():
    table = request.args.get("tb")

    get_request = extract_records(table)

    if not get_request["status"]:
        if get_request["error"] == 'Table not found':
            resp = make_response(jsonify({'error': get_request["error"]}), 409)
            return resp

        resp = make_response(jsonify({'error': 'Server error'}), 500)
        return resp

    resp = make_response(jsonify({'data':get_request["list"]}), 200)
    return resp

@app.route("/get/list")
def get_list():
    table = request.args.get("tb")
    identifier_key = request.args.get("key")
    identifier_value = request.args.get("value")

    list_request = extract_record_list(table, identifier_key, identifier_value)

    if not list_request["status"]:
        if list_request["error"] == 'Record not found':
            resp = make_response(jsonify({'error': list_request["error"]}), 409)
            return resp

        resp = make_response(jsonify({'error': 'Server error'}), 500)
        return resp
    
    resp = make_response(jsonify({'data':list_request["list"]}), 200)
    return resp

@app.route("/modify", methods=["PUT"])
def modify():
    if request.method != 'PUT':
        resp = make_response(jsonify({'error':'Request method not allowed'}), 405)
        return resp

    rdata = request.get_json()
    table = rdata["tb"]
    identifier_key = rdata["idkey"]
    identifier_value = rdata["idvalue"]
    column_name = rdata["column_name"]
    column_value = rdata["column_value"]

    if column_name in ['pswd']:
        column_value = data_cryptographer('ec', column_value)

    modification_request = modify_record(table, identifier_key, identifier_value, column_name, column_value)

    if not modification_request["status"]:
        if modification_request["error"] == 'Record not found':
            resp = make_response(jsonify({'error': modification_request["error"]}), 409)
            return resp

        resp = make_response(jsonify({'error': 'Server error'}), 500)
        return resp
    
    resp = make_response(jsonify({'data':'Record modified'}), 200)
    return resp

@app.route("/reset", methods=["POST"])
def reset():
    if request.method != 'POST':
        resp = make_response(jsonify({'error':'Request method not allowed'}), 405)
        return resp

    rdata = request.get_json()
    table = rdata["tb"]
    identifier_key = rdata["col"]
    identifier_value = rdata["id"]

    identity_request = extract_record(table, identifier_key, identifier_value)

    if not identity_request["status"]:
        if identity_request["error"] == 'Record not found':
            resp = make_response(jsonify({'error': identity_request["error"]}), 409)
            return resp

        resp = make_response(jsonify({'error': 'Server error'}), 500)
        return resp

    if identity_request["object"] != None:
        reset_code = random_gen(8)
        email = identity_request["object"][3]
        fname = identity_request["object"][1]

        # Send Welcome email to student
        __mail_request = send_mail(2, email, {'f_name':fname, 'reset_code':reset_code})

        if not __mail_request['status']:
            resp = make_response(jsonify({'error':'Mail sending failed!'}), 501)
            return resp

        resp = make_response(jsonify({'c': reset_code}), 200)
        return resp

    resp = make_response(jsonify({'note':'Record not found'}), 409)
    return resp

@app.route("/add/room", methods=["POST"])
def add_room():
    if request.method != 'POST':
        resp = make_response(jsonify({'error':'Request method not allowed'}), 405)
        return resp

    rdata = request.get_json()
    room_admin = rdata["rm_adn"]
    room_title = rdata["tle"]
    room_type = rdata["tp"]

    if not room_admin or not room_title:
        resp = make_response(jsonify({'error': 'Missing params'}), 400)
        return resp

    room_id = random_gen(8)

    # Check if user is creating a group or a class room
    if room_type == 'class':
        check_if_teacher = extract_record('teachers', 'teacher_id', room_admin)

        if not check_if_teacher["status"] or check_if_teacher["object"] == None:
            resp = make_response(jsonify({'error': 'Authenticator not allowed'}), 403)
            return resp
        

    group_dict = {
        'room_id': room_id,
        'room_title': room_title,
        'room_type': room_type,
        'room_admin': room_admin
    }

    group_request = add_record('rooms', group_dict)

    if not group_request["status"]:
        if group_request["error"] == 'Record not found':
            resp = make_response(jsonify({'error': 'Group with group ID already exists'}), 409)
            return resp

        resp = make_response(jsonify({'error': 'Server error'}), 500)
        return resp

    resp = make_response(jsonify({'id': room_id}), 201)
    return resp

@app.route("/add/activies", methods=["POST"])
def activities():
    if request.method != 'POST':
        resp = make_response(jsonify({'error':'Request method not allowed'}), 405)
        return resp
    
    rdata = request.get_json()
    room_id = rdata["rmid"]
    room_admin = rdata["rmadn"]
    member_id = rdata["mid"]
    member_role = rdata["mrl"]
    status = 0

    activity_object = {
        'room_id': room_id, 
        'room_admin': room_admin, 
        'member_id': member_id, 
        'member_role': member_role, 
        'status': status
    }

    activity_request = add_record('room_activities', activity_object)

    if not activity_request["status"]:
        resp = make_response(jsonify({'error': 'Server error'}), 500)
        return resp

    resp = make_response(jsonify({'note': 'Activity added'}), 201)
    return resp
