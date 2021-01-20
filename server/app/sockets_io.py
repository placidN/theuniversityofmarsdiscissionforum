import time

from app import app, socketio, join_room, leave_room
from app.functions import data_cryptographer, random_gen
from app.db_config import add_record, remove_record, modify_record, extract_records, extract_record_data, extract_record, extract_record_list, activity_in_room



@socketio.on('join_room')
def handle_join_room_event(data):
    # Collect member ID and room ID then verify
    member_id = data['member_id']
    room_id = data['room_id']

    check_if_invited = activity_in_room('check', member_id, room_id)

    if check_if_invited["status"]:

        if check_if_invited["list"][4] == 0:

            # toggle room activity status for this member in this room
            activity_in_room('update', member_id, room_id)

            join_room(room_id)
            socketio.emit('join_announcement', data, room=room_id)

        join_room(room_id)


@socketio.on('send_message')
def handle_send_message_event(data):
    message_id = random_gen(8)

    # Backup chats on the datacase
    values = {
        'message_id': message_id, 
        'room_id': data["room_id"], 
        'member_id': data["member_id"], 
        'message': data["message"],
        'time': time.time()
    }
    add_record('messages', values)
    data['time'] = time.time()
    socketio.emit('receive_message', data, room=data['room_id'])

@socketio.on('leave_room')
def handle_leave_room_event(data):
    member_id = data["member_id"]
    room_id = data["room_id"]

    request_remove = activity_in_room('remove', member_id, room_id)

    if request_remove["status"]:
        socketio.emit('leave_room_announcement', data, room=data['room_id'])