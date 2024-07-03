import os

from flask import render_template, redirect, send_file

from app import create_app, db
from app.models import User, Product, CartItem

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Product': Product, 'CartItem': CartItem}


@app.route('/documentation')
def documentation():
    return render_template("index.html")


@app.route('/documentation/types')
def documentation_types():
    return send_file("templates/types", as_attachment=True)


@app.route('/')
def index():
    return redirect("/documentation")


if __name__ == '__main__':
    app.run(debug=True,host="192.168.0.94", port="80")
