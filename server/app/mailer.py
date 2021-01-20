from app import app
from app.mail_config import SendMail

def send_mail(message_choice, receiver, placeholders):
    
    message_data = [
        {
            'subject': 'Welcome',
            'sender': app.config['EMAIL_USER'],
            'sender_id': 'University of Mars',
            'msg_content' : 'contents/welcome.html',
            'placeholders' : (
                {
                    'key':'[FIRST_NAME]',
                    'value':str(placeholders['f_name']) if 'f_name' in placeholders else ''
                },
                {
                    'key':'[ROLE]',
                    'value':str(placeholders['role']) if 'role' in placeholders  else ''
                },
                {
                    'key':'[ROLE_NOTE]',
                    'value':str(placeholders['role_note']) if 'role_note' in placeholders  else ''
                },
                {
                    'key':'[ID]',
                    'value':str(placeholders['id']) if 'id' in placeholders  else ''
                },
                {
                    'key':'[EMAIL]',
                    'value':str(placeholders['email']) if 'email' in placeholders  else ''
                }
            )
        },
        {
            'subject': 'Email Verification',
            'sender': app.config['EMAIL_USER'],
            'sender_id': 'University of Mars',
            'msg_content' : 'contents/email_v.html',
            'placeholders' : [
                {
                    'key':'[VERIFICATION_CODE]',
                    'value':str(placeholders['verification_link']) if 'verification_link' in placeholders  else ''
                },
                {
                    'key':'[EMAIL]',
                    'value':str(placeholders['email']) if 'email' in placeholders  else ''
                },
                {
                    'key':'[ROLE]',
                    'value':str(placeholders['role']) if 'role' in placeholders  else ''
                }
            ]
        },
        {
            'subject': 'Reset Password',
            'sender': app.config['EMAIL_USER'],
            'sender_id': 'University of Mars',
            'msg_content' : 'contents/reset.html',
            'placeholders' : (
                {
                    'key':'[FIRST_NAME]',
                    'value':str(placeholders['f_name']) if 'f_name' in placeholders  else ''
                },
                {
                    'key':'[RESET_CODE]',
                    'value':str(placeholders['reset_code']) if 'reset_code' in placeholders  else ''
                }
            )
        }
    ]

    message_data = message_data[message_choice]

    __mailer = SendMail(message_data['subject'])
    __mailer.set_content(message_data['msg_content'], message_data['placeholders'])
    __mailer.set_sender(message_data['sender'])
    __mailer.set_sender_id(message_data['sender_id'])
    __mailer.set_receiver(receiver)
    __mail_sent = __mailer.send()

    if __mail_sent['status']:
        return {'status':True, 'response':'Mail sent!'}
    else:
        return {'status':False, 'error':'Mail sending failed!', 'reason':__mail_sent["err"]}