from flask import Flask, request, abort
import git
import hashlib
import hmac
import os

app = Flask(__name__)


@app.route("/")
def index():
    return "Hello World!"


@app.route("/update_server", methods=["POST"])
def webhook():
    if request.method == "POST":
        try:
            payload = validate_request(request)
            repo = git.Repo("/home/pi/Documents/git-repos/pi_deploy")
            origin = repo.remotes.origin
            origin.pull()
            return "Updated PythonAnywhere successfully", 200
        except Exception as e:
           raise Exception(e) 
    else:
        return "Wrong event type", 400


def validate_request(req):
    abort_code = 418
    x_hub_signature = req.headers.get("X-Hub-Signature")
    if not is_valid_signature(x_hub_signature, req.data):
        print(f"Deploy signature failed: {x_hub_signature}")
        abort(abort_code)

    payload = req.get_json()
    if payload is None:
        print(f"Payload is empty: {payload}")
        abort(abort_code)

    return payload


def is_valid_signature(x_hub_signature, data, private_key=os.getenv("SECRET_KEY")):
    """Verify webhook signature.
    """
    hash_algorithm, github_signature = x_hub_signature.split("=", 1)
    algorithm = hashlib.__dict__.get(hash_algorithm)
    encoded_key = bytes(private_key, "latin-1")
    mac = hmac.new(encoded_key, msg=data, digestmod=algorithm)

    return hmac.compare_digest(mac.hexdigest(), github_signature)
