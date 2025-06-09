
import os
import extract_msg
import email
from email import policy
from email.parser import BytesParser
from pathlib import Path

def process_msg_file(msg_path, temp_dir):
    msg = extract_msg.Message(msg_path)
    body_text = msg.body or "No body found."
    attachments = []

    base_name = Path(msg_path).stem
    body_txt_path = os.path.join(temp_dir, f"{base_name}_body.txt")
    with open(body_txt_path, "w", encoding="utf-8") as f:
        f.write(body_text)

    # Save attachments
    for att in msg.attachments:
        filename = att.longFilename or att.shortFilename
        if filename:
            att_path = os.path.join(temp_dir, filename)
            with open(att_path, 'wb') as f:
                f.write(att.data)
            attachments.append(att_path)

    return body_txt_path, attachments


def process_eml_file(eml_path, temp_dir):
    with open(eml_path, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)

    body_text = msg.get_body(preferencelist=('plain')).get_content() if msg.get_body() else "No body text found."
    base_name = Path(eml_path).stem
    body_txt_path = os.path.join(temp_dir, f"{base_name}_body.txt")
    with open(body_txt_path, "w", encoding="utf-8") as f:
        f.write(body_text)

    attachments = []
    for part in msg.iter_attachments():
        filename = part.get_filename()
        if filename:
            att_path = os.path.join(temp_dir, filename)
            with open(att_path, 'wb') as f:
                f.write(part.get_content())
            attachments.append(att_path)

    return body_txt_path, attachments
