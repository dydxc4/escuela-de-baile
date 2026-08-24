from os import path
import uuid

def generate_uuid_filename(instance, filename):
    ext = path.splitext(filename)[1].lower()
    new_filename = f'{uuid.uuid4()}{ext}'

    return path.join('uploads', new_filename)
