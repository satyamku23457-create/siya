from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import os
import json
import base64
import resend

# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
RESPONSE_FILE = os.path.join(BASE_DIR, "responses.json")

# =========================================================
# ENV
# =========================================================

load_dotenv(
    os.path.join(BASE_DIR, ".env")
)

# =========================================================
# FLASK
# =========================================================

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR
)

# =========================================================
# RESEND CONFIG
# =========================================================

RESEND_API_KEY = os.getenv(
    "RESEND_API_KEY"
)

RESEND_FROM_EMAIL = os.getenv(
    "RESEND_FROM_EMAIL",
    "onboarding@resend.dev"
)

# Your Resend account email
TO_EMAIL = "satyamku23457@gmail.com"

if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY
else:
    print("❌ RESEND_API_KEY is missing.")

# =========================================================
# BACKGROUND WORKER
# =========================================================

executor = ThreadPoolExecutor(
    max_workers=2
)

# =========================================================
# SAVE RESPONSE
# =========================================================

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


# =========================================================
# SEND YES / NO EMAIL
# =========================================================

def send_response_email(item):

    if not RESEND_API_KEY:

        print(
            "❌ RESEND_API_KEY missing."
        )

        return

    if item["answer"] == "YES":

        subject = "❤️ SIYA CHOSE YES!"

        body = f"""
❤️ PROPOSAL RESPONSE

Siya clicked YES ❤️

Time:
{item["time"]}

Your proposal website received a YES response.
"""

    else:

        subject = "💙 SIYA CHOSE NO"

        body = f"""
💙 PROPOSAL RESPONSE

Siya clicked NO.

Time:
{item["time"]}

Your proposal website received a NO response.
"""

    try:

        result = resend.Emails.send({

            "from": RESEND_FROM_EMAIL,

            "to": [
                TO_EMAIL
            ],

            "subject": subject,

            "text": body
        })

        print(
            "✅ RESPONSE EMAIL SENT:"
        )

        print(result)

    except Exception as e:

        print(
            "❌ RESEND RESPONSE EMAIL ERROR:"
        )

        print(
            repr(e)
        )


# =========================================================
# SEND PHOTO EMAIL
# =========================================================

def send_photo_email(attachments):

    if not RESEND_API_KEY:

        print(
            "❌ RESEND_API_KEY missing."
        )

        return

    try:

        result = resend.Emails.send({

            "from": RESEND_FROM_EMAIL,

            "to": [
                TO_EMAIL
            ],

            "subject":
                "💗 Photos from Siya Proposal",

            "text":
                """
❤️ PHOTOS FROM SIYA PROPOSAL

Photos were selected and sent
through the proposal website.

Someone completed the little game
and chose to share these photos. ❤️
""",

            "attachments":
                attachments
        })

        print(
            "✅ PHOTO EMAIL SENT:"
        )

        print(result)

    except Exception as e:

        print(
            "❌ RESEND PHOTO EMAIL ERROR:"
        )

        print(
            repr(e)
        )


# =========================================================
# PAGES
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


@app.route("/real-proposal")
def real_proposal():

    return render_template(
        "real-proposal.html"
    )


@app.route("/page-3")
def page_3():

    return render_template(
        "page-3.html"
    )


@app.route("/final-proposal")
def final_proposal():

    return render_template(
        "final-proposal.html"
    )


@app.route("/page-5")
def page_5():

    return render_template(
        "page-5.html"
    )


@app.route("/last-surprise")
def last_surprise():

    return render_template(
        "last-surprise.html"
    )


# =========================================================
# PING
# =========================================================

@app.route("/ping")
def ping():

    return jsonify({

        "success": True,

        "message":
            "Siya Proposal Server is awake ❤️"
    })


# =========================================================
# YES / NO RESPONSE
# =========================================================

@app.route(
    "/response",
    methods=["POST"]
)
def response():

    try:

        data = request.get_json(
            silent=True
        )

        if not data:

            return jsonify({

                "success": False,

                "message":
                    "Invalid request."
            }), 400

        answer = data.get(
            "answer"
        )

        if answer not in [
            "YES",
            "NO"
        ]:

            return jsonify({

                "success": False,

                "message":
                    "Invalid answer."
            }), 400

        item = save_response(
            answer
        )

        executor.submit(
            send_response_email,
            item
        )

        return jsonify({

            "success": True,

            "answer":
                answer
        }), 200

    except Exception as e:

        print(
            "❌ RESPONSE ERROR:",
            repr(e)
        )

        return jsonify({

            "success": False,

            "message":
                "Something went wrong."
        }), 500


# =========================================================
# GAME RESPONSE
# =========================================================

@app.route(
    "/game-response",
    methods=["POST"]
)
def game_response():

    try:

        data = request.get_json(
            silent=True
        )

        if not data:

            data = {}

        print(
            "🎮 GAME RESPONSE:",
            data
        )

        return jsonify({

            "success": True,

            "message":
                "Game response received."
        }), 200

    except Exception as e:

        print(
            "❌ GAME RESPONSE ERROR:",
            repr(e)
        )

        return jsonify({

            "success": False,

            "message":
                "Game response failed."
        }), 500


# =========================================================
# SEND PHOTOS
# =========================================================

@app.route(
    "/send-photos",
    methods=["POST"]
)
def send_photos():

    photos = request.files.getlist(
        "photos"
    )

    if len(photos) > 10:

        return jsonify({

            "success": False,

            "message":
                "Maximum 10 photos allowed."
        }), 400

    if not photos:

        return jsonify({

            "success": False,

            "message":
                "No photos selected."
        }), 400

    if not RESEND_API_KEY:

        return jsonify({

            "success": False,

            "message":
                "Resend API key is missing."
        }), 500

    try:

        attachments = []

        for photo in photos:

            if not photo:
                continue

            if not photo.filename:
                continue

            mimetype = (
                photo.mimetype or ""
            )

            if not mimetype.startswith(
                "image/"
            ):

                print(
                    "Skipped non-image:",
                    photo.filename
                )

                continue

            data = photo.read()

            if not data:
                continue

            encoded_data = (
                base64.b64encode(data)
                .decode("utf-8")
            )

            attachments.append({

                "filename":
                    photo.filename,

                "content":
                    encoded_data
            })

        if not attachments:

            return jsonify({

                "success": False,

                "message":
                    "No valid images selected."
            }), 400

        executor.submit(
            send_photo_email,
            attachments
        )

        return jsonify({

            "success": True,

            "count":
                len(attachments),

            "message":
                "Photos are being sent."
        }), 200

    except Exception as e:

        print(
            "❌ PHOTO PROCESSING ERROR:",
            repr(e)
        )

        return jsonify({

            "success": False,

            "message":
                "Photos could not be sent."
        }), 500


# =========================================================
# SERVER
# =========================================================

if __name__ == "__main__":

    print("")
    print(
        "=============================="
    )

    print(
        "❤️ SIYA PROPOSAL SERVER"
    )

    print(
        "=============================="
    )

    print(
        "Templates:",
        TEMPLATE_DIR
    )

    print(
        "Resend configured:",
        bool(RESEND_API_KEY)
    )

    print(
        "From:",
        RESEND_FROM_EMAIL
    )

    print(
        "To:",
        TO_EMAIL
    )

    print(
        "=============================="
    )

    print("")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )