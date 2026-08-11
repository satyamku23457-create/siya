from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from datetime import datetime
from email.message import EmailMessage
import os
import json
import smtplib


# =========================
# PATHS + ENVIRONMENT
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

load_dotenv(os.path.join(BASE_DIR, ".env"))


# =========================
# FLASK APP
# =========================

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR
)


# =========================
# CONFIG
# =========================

SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

TO_EMAIL = "satyamku23457@gmail.com"

RESPONSE_FILE = os.path.join(
    BASE_DIR,
    "responses.json"
)


# =========================
# SAVE PROPOSAL RESPONSE
# =========================

def save_response(answer):

    data = []

    if os.path.exists(RESPONSE_FILE):

        try:
            with open(
                RESPONSE_FILE,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

                if not isinstance(data, list):
                    data = []

        except Exception:
            data = []

    item = {
        "answer": answer,
        "time": datetime.now().strftime(
            "%d %B %Y, %I:%M:%S %p"
        )
    }

    data.append(item)

    with open(
        RESPONSE_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False
        )

    return item


# =========================
# SEND EMAIL
# =========================

def send_message_email(message):

    if not SMTP_EMAIL or not SMTP_PASSWORD:

        print(
            "❌ SMTP_EMAIL or SMTP_PASSWORD "
            "missing in .env"
        )

        return False

    try:

        with smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465,
            timeout=20
        ) as smtp:

            smtp.login(
                SMTP_EMAIL,
                SMTP_PASSWORD
            )

            smtp.send_message(message)

        return True

    except Exception as e:

        print(
            "❌ EMAIL ERROR:",
            e
        )

        return False


# =========================
# YES / NO EMAIL
# =========================

def send_response_email(item):

    if item["answer"] == "YES":

        subject = "❤️ SIYA CHOSE YES!"

        body = f"""
❤️ PROPOSAL RESPONSE

Siya clicked YES ❤️

Time:
{item["time"]}
"""

    else:

        subject = "💙 SIYA CHOSE NO"

        body = f"""
💙 PROPOSAL RESPONSE

Siya clicked NO.

Time:
{item["time"]}
"""

    message = EmailMessage()

    message["Subject"] = subject
    message["From"] = SMTP_EMAIL
    message["To"] = TO_EMAIL

    message.set_content(body)

    success = send_message_email(message)

    if success:
        print("✅ Response email sent successfully.")

    return success


# =========================
# PAGES
# =========================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/real-proposal")
def real_proposal():
    return render_template("real-proposal.html")


@app.route("/page-3")
def page_3():
    return render_template("page-3.html")


@app.route("/final-proposal")
def final_proposal():
    return render_template("final-proposal.html")


@app.route("/page-5")
def page_5():
    return render_template("page-5.html")


@app.route("/last-surprise")
def last_surprise():
    return render_template("last-surprise.html")


# =========================
# YES / NO RESPONSE
# =========================

@app.route("/response", methods=["POST"])
def response():

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "message": "Invalid request."
            }), 400

        answer = data.get("answer")

        if answer not in ["YES", "NO"]:
            return jsonify({
                "success": False,
                "message": "Invalid answer."
            }), 400

        item = save_response(answer)

        send_response_email(item)

        return jsonify({
            "success": True,
            "answer": answer
        })

    except Exception as e:

        print(
            "❌ RESPONSE ERROR:",
            e
        )

        return jsonify({
            "success": False,
            "message": "Something went wrong."
        }), 500


# =========================
# SEND SELECTED PHOTOS
# =========================

@app.route("/send-photos", methods=["POST"])
def send_photos():

    photos = request.files.getlist("photos")

    # =========================
    # MAXIMUM 10 PHOTOS
    # =========================

    if len(photos) > 10:

        return jsonify({
            "success": False,
            "message": "Maximum 10 photos allowed."
        }), 400

    # =========================
    # NO PHOTOS
    # =========================

    if not photos:

        return jsonify({
            "success": False,
            "message": "No photos selected."
        }), 400

    # =========================
    # CHECK EMAIL SETTINGS
    # =========================

    if not SMTP_EMAIL or not SMTP_PASSWORD:

        return jsonify({
            "success": False,
            "message": "Email settings are missing."
        }), 500

    try:

        message = EmailMessage()

        message["Subject"] = (
            "💗 Photos from Siya Proposal"
        )

        message["From"] = SMTP_EMAIL
        message["To"] = TO_EMAIL

        message.set_content(
            """
❤️ PHOTOS FROM SIYA PROPOSAL

Photos were selected and sent
through the proposal website.

Someone completed the little game
and chose to share these photos. ❤️
"""
        )

        attached_count = 0

        # =========================
        # ATTACH PHOTOS
        # =========================

        for photo in photos:

            if not photo:
                continue

            if not photo.filename:
                continue

            mimetype = photo.mimetype or ""

            # Only allow images
            if not mimetype.startswith("image/"):

                print(
                    "Skipped non-image:",
                    photo.filename
                )

                continue

            data = photo.read()

            if not data:
                continue

            subtype = mimetype.split(
                "/",
                1
            )[1]

            message.add_attachment(
                data,
                maintype="image",
                subtype=subtype,
                filename=photo.filename
            )

            attached_count += 1

        # =========================
        # NO VALID IMAGES
        # =========================

        if attached_count == 0:

            return jsonify({
                "success": False,
                "message": "No valid images selected."
            }), 400

        # =========================
        # SEND EMAIL
        # =========================

        with smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465,
            timeout=20
        ) as smtp:

            smtp.login(
                SMTP_EMAIL,
                SMTP_PASSWORD
            )

            smtp.send_message(message)

        print(
            f"✅ {attached_count} photo(s) "
            "sent successfully."
        )

        return jsonify({
            "success": True,
            "count": attached_count,
            "message": "Photos sent successfully."
        })

    except Exception as e:

        print(
            "❌ PHOTO EMAIL ERROR:",
            e
        )

        return jsonify({
            "success": False,
            "message": "Email could not be sent."
        }), 500


# =========================
# RUN SERVER
# =========================

if __name__ == "__main__":

    print("")
    print("==============================")
    print("❤️ SIYA PROPOSAL SERVER")
    print("==============================")
    print(
        "Templates:",
        TEMPLATE_DIR
    )
    print(
        "Server: http://localhost:5000"
    )
    print(
        "Last Surprise:"
    )
    print(
        "http://localhost:5000/last-surprise"
    )
    print("==============================")
    print("")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )