from flask import Blueprint, render_template

authBp = Blueprint("auth", __name__)

@authBp.route("/login")
def login():
    return render_template("login.html")
