## If aiming to use a certain library. Then check if this library needs to be put in
## the requirements.txt file then the requirements.txt file needs to be executed
from flask import Flask, render_template, request, url_for, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from flask_ckeditor import CKEditorField # Currently for some reason when CkEditor form with
# being able to customize the message of the form a lot such as by using images or etc is 
# created it shows something like CkEditor is insecure. So this fully fledge form of Ckeditor is 
# not used in this project. Instead a simple Ckeditor form is used
from wtforms.validators import DataRequired
from flask_wtf.csrf import CSRFProtect
# from flask_ckeditor import CKEditor
from flask_bootstrap import Bootstrap5

import os
import smtplib
from datetime import date
import sqlite3
# from flask_sqlalchemy import SQLAlchemy



class ContactFrom(FlaskForm):
    email = StringField(label="Email", validators=[DataRequired()])
    name = StringField(label="Name", validators=[DataRequired()])
    # message = StringField(label="Message", validators=[DataRequired()])
    message = CKEditorField(label="Message", validators=[DataRequired()])
    submit_button = SubmitField("Submit")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv('FLASK_KEY')
# CKEditor(app)
Bootstrap5(app)
CSRFProtect(app)

email = os.getenv("EMAIL")
password_var = os.getenv("PASSW")

# List of dictionaries that stores data from the database
list_of_diction = []
connection = sqlite3.connect('instance/projects.db')
cursor_var = connection.cursor()
cursor_var.execute("SELECT * FROM projects")
rows = cursor_var.fetchall()
for num in range(0, len(rows)):
    list_of_diction.append({
        "id": rows[num][0],
        "title": rows[num][1],
        "subtitle": rows[num][2],
         "brief": rows[num][3],
         "body": rows[num][4],
         "img_id": rows[num][5],
         "vid_id": rows[num][6],
    })

@app.context_processor
def current_time():
    return {
        "current_yr": date.today().year,
    }

@app.route('/', methods=['GET', 'POST'])
def home_pg_func():
    contact_obj = ContactFrom()
    if request.method == 'GET':
        # coming_soon = "Coming-soon.png"
        return render_template(
            template_name_or_list="home.html",
            message_form = contact_obj,
            # img_var=coming_soon,
            projects_list=list_of_diction,
            ) 
    else:
        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            connection.login(
                user=email,
                password=password_var
                ) 
            connection.sendmail(
                from_addr=email,
                to_addrs=email,
                msg=f"Subject: Message from {request.form.get('email')}\n"+request.form.get('message')
                +f"\n\nContact Details of User:\n- Name: {request.form.get('name')}\n- Email: {request.form.get('email')}")
        return redirect(url_for('success_func'))

@app.route('/projects/<int:element_num>')
def projects_func(element_num):
    return render_template(template_name_or_list="projects.html", projects_list=list_of_diction[element_num])#, vids_id = video_id)

@app.route('/success', methods=['GET', 'POST'])
def success_func():
    if request.method == 'GET':
        return render_template(template_name_or_list="success.html")
    elif request.method != 'GET' and request.method != 'POST':
        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            connection.login(
                user=email,
                password=password_var
                ) 
            connection.sendmail(
                from_addr=email,
                to_addrs=email,
                msg="Subject: Site Error\nSite Error with Contact Form Filled Out by the User"
            )

        return render_template(template_name_or_list="denied.html")
    

if __name__ == "__main__":
    app.run(debug=False)