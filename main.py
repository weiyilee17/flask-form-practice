from datetime import datetime

from flask import Flask, render_template, request, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from os import getenv
from flask_mail import Mail, Message

app = Flask(__name__)

app.config["SECRET_KEY"] = getenv('FLASK_SECRET_KEY')
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["MAIL_SERVER"] = 'smtp.gmail.com'
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = getenv('EMAIL_SENDER')
app.config["MAIL_PASSWORD"] = getenv('PORTFOLIO_APP_PASSWORD')

db = SQLAlchemy(app)
mail = Mail(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    email = db.Column(db.String(80))
    date = db.Column(db.Date)
    occupation = db.Column(db.String(80))


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        date = request.form['date']
        date_object = datetime.strptime(date, '%Y-%m-%d')
        occupation = request.form['occupation']
        user = User(first_name=first_name, last_name=last_name, email=email, date=date_object, occupation=occupation)

        db.session.add(user)
        db.session.commit()

        email_body = f'Thank you for your submission, {first_name}. Here are your data: \n' \
                     f'{first_name}\n' \
                     f'{last_name}\n' \
                     f'{date}\n' \
                     f'{occupation}\n' \
                     'Thank you!'

        message = Message(subject='New Form Submission', sender=app.config['MAIL_USERNAME'], recipients=[email],
                          body=email_body)

        mail.send(message)

        flash(f'{first_name}, your form was submitted successfully!', 'success')
        """Without the return redirect, after the from submits the post request, it reloads. The browser remembers 
        the last request was post, so posts again on reload, so not only we would have 2 entries for only submitting 
        once, we would also have the alert text for the previous user's submission"""
        return redirect('/')

    return render_template('index.html')


if __name__ == '__main__':
    with app.app_context():
        # Creates instances/data.db if doesn't exist
        db.create_all()
        app.run(debug=True, port=5001)
