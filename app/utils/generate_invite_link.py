import secrets
from app.models import InviteLink
from app import db

def generate_invite_link(class_id):
    token = secrets.token_hex(16)
    new_link = InviteLink(class_id=class_id, token=token)
    db.session.add(new_link)
    db.session.commit()
    return f"https://phonegetter.onrender.com/classes/class/{class_id}/invite/{token}"