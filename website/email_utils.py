from flask_mail import Message
from flask import url_for
from . import mail

def send_reset_email(user):
    token = user.get_reset_token()
    reset_url = url_for('auth.reset_token', token=token, _external=True)
    msg = Message('Password Reset Request',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:

{reset_url}

If you did not make this request, simply ignore this email.
'''
    mail.send(msg)