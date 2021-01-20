import sqlite3
from app import app

base = 'example.db'

if app.config['ENV'] == 'development':
    base = ':memory:'


conn = sqlite3.connect(base)
cursor = conn.cursor()

# Create table

with conn:

    # Create students table
    cursor.execute('''CREATE TABLE IF NOT EXISTS students
                    (
                        student_id TEXT PRIMARY KEY UNIQUE,
                        first_name TEXT,
                        last_name TEXT,
                        email TEXT UNIQUE,
                        pswd TEXT,
                        level INTEGER,
                        profile_photo BLOB,
                        verified INTEGER
                    )
                ''')

    # Create teachers table
    cursor.execute('''CREATE TABLE IF NOT EXISTS teachers
                    (
                        teacher_id TEXT PRIMARY KEY UNIQUE, 
                        first_name TEXT, 
                        last_name TEXT, 
                        email TEXT UNIQUE, 
                        pswd TEXT,
                        profile_photo BLOB,
                        verified INTEGER
                    )
                ''')

    # Create rooms table
    cursor.execute('''CREATE TABLE IF NOT EXISTS rooms
                    (
                        room_id TEXT PRIMARY KEY UNIQUE, 
                        room_title TEXT UNIQUE, 
                        room_type TEXT, 
                        room_admin TEXT
                    )
                ''')

    # Create room_activities table
    cursor.execute('''CREATE TABLE IF NOT EXISTS room_activities
                    (
                        room_id TEXT PRIMARY KEY, 
                        room_admin TEXT,
                        member_id TEXT,
                        member_role TEXT,
                        status INTEGER
                    )
                ''')

    # Create messages table
    cursor.execute('''CREATE TABLE IF NOT EXISTS messages
                    (
                        message_id TEXT PRIMARY KEY,
                        room_id TEXT,
                        member_id TEXT,
                        message TEXT,
                        time REAL
                    )
                ''')

def add_record(table, values):
    print(table)
    sql = ''
    if table == 'students':
        sql = "INSERT INTO students VALUES (:student_id, :first_name, :last_name, :email, :pswd, :level, :profile_photo, :verified)"

    if table == 'teachers':
        sql = "INSERT INTO teachers VALUES (:teacher_id, :first_name, :last_name, :email, :pswd, :profile_photo, :verified)"

    if table == 'rooms':
        sql = "INSERT INTO rooms VALUES (:room_id, :room_title, :room_type, :room_admin)"

    if table == 'room_activities':
        sql = "INSERT INTO room_activities VALUES (:room_id, :room_admin, :member_id, :member_role, :status)"

    if table == 'messages':
        sql = "INSERT INTO messages VALUES (:message_id, :room_id, :member_id, :message)"

    try:
        cursor.execute(sql, values)
        conn.commit()
        return {'status':True}

    except sqlite3.ProgrammingError as err:
        print(err)
        return {'status':False, 'error': 'Record exists'}

    except sqlite3.Error as err:
        print(err)
        return {'status':False, 'error': err}
        

def remove_record(table, validator, identifier):
    id_obj = {
        'id':identifier
    }

    sql = "DELETE FROM {} WHERE {} = :id".format(table, validator)

    try:
        cursor.execute(sql, id_obj)
        conn.commit()
        return {'status':True}

    except sqlite3.ProgrammingError as err:
        return {'status':False, 'error': 'Record not found'}

    except sqlite3.Error as err:
        return {'status':False, 'error': err}

def modify_record(table, identifier_key, identifier_value, column, value):
    id_obj = {
        'identifier':identifier_value,
        'value': value
    }

    sql = "UPDATE {} SET {} = :value WHERE {} = :identifier".format(table, column, identifier_key)
    try:
        cursor.execute(sql, id_obj)
        conn.commit()
        return {'status':True}

    except sqlite3.ProgrammingError as err:
        return {'status':False, 'error':'Record not found'}

    except sqlite3.Error as err:
        return {'status':False, 'error': err}

def extract_records(table):
    sql = "SELECT * FROM {}".format(table)

    try:
        cursor.execute(sql)
        list_data = cursor.fetchall()

        return {'status':True, 'list':list_data}

    except sqlite3.ProgrammingError:
        return {'status':False, 'error':'Table not found'}

    except sqlite3.Error as err:
        return {'status':False, 'error':'Server error'}

def extract_record_data(table, identifier_key, identifier_value, column):
    id_obj = {
        'identifier': identifier_value
    }
    sql = "SELECT {} FROM {} WHERE {} = :identifier".format(column, table, identifier_key)

    try:
        cursor.execute(sql, id_obj)
        list_data = cursor.fetchone()
        return {'status':True, 'object':list_data}

    except sqlite3.ProgrammingError as err:
        return {'status':False, 'error': 'Record not found'}

    except sqlite3.Error as err:
        return {'status':False, 'error': err}

def extract_record(table, identifier_key, identifier_value):
    id_obj = {
        'identifier':identifier_value
    }
    sql = "SELECT * FROM {} WHERE {} = :identifier".format(table, identifier_key)

    try:
        cursor.execute(sql, id_obj)
        list_data = cursor.fetchone()
        return {'status':True, 'object':list_data}

    except sqlite3.ProgrammingError as err:
        return {'status':False, 'error':'Record not found'}

    except sqlite3.Error as err:
        return {'status':False, 'error': err}

def extract_record_list(table, identifier_key, identifier_value):
    id_obj = {
        'identifier':identifier_value
    }
    sql = "SELECT * FROM {} WHERE {} = :identifier".format(table, identifier_key)

    try:
        cursor.execute(sql, id_obj)
        list_data = cursor.fetchall()
        return {'status':True, 'list':list_data}

    except sqlite3.ProgrammingError as err:
        return {'status':False, 'error':'Record not found'}

    except sqlite3.Error as err:
        return {'status':False, 'error': err}

def activity_in_room(mode, member_id, room_id):
    if mode == 'check':
        values = {
            'member_id': member_id,
            'room_id': room_id
        }
        sql = "SELECT * FROM room_activities WHERE member_id = :member_id AND room_id = :room_id"

        try:
            cursor.execute(sql, values)
            list_data = cursor.fetchone()
            return {'status':True, 'list':list_data}

        except sqlite3.ProgrammingError as err:
            return {'status':False, 'error':'Record not found'}

        except sqlite3.Error as err:
            return {'status':False, 'error': err}

    if mode == 'update':
        values = {
            'member_id':member_id,
            'room_id': room_id,
            'status': 1
        }

        sql = "UPDATE room_activities SET status = :status WHERE member_id = :member_id AND room_id = :room_id"

        try:
            cursor.execute(sql, values)
            conn.commit()
            return {'status':True}

        except sqlite3.ProgrammingError as err:
            return {'status':False, 'error':'Record not found'}

        except sqlite3.Error as err:
            return {'status':False, 'error': err}

    if mode == 'remove':
        sql = "DELETE FROM room_activities WHERE member_id = :member_id AND room_id = :room_id"

        try:
            cursor.execute(sql, {'member_id': member_id, 'room_id':room_id})
            cursor.commit()
            return {'status':True}
        
        except sqlite3.ProgrammingError:
            return {'status':False, 'error':'Record not found'}

        except sqlite3.Error as err:
            return {'status':False, 'error': err}
