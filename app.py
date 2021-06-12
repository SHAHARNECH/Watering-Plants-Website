from flask import Flask, render_template, json, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__)
# MySQL configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users_db'

db = SQLAlchemy(app)
message=""


class Event():
    which_plant=""
    plant_id=0
    date= date.today()
    visited= 'False'
    def __repr__(self):
        return "'which_plant': %s, 'plant_id': %d, 'date' : %s, 'visited' : %s " %(self.which_plant, self.plant_id, self.date, self.visited)


class User(db.Model):
    __tablename__ = 'user'
    name=db.Column(db.String(200), nullable=False)
    email= db.Column(db.String(200),primary_key=True, nullable=False)
    password= db.Column(db.String(10), nullable=False)
    plants_list = db.Column(db.PickleType, nullable=True)
    user_events=db.Column(db.PickleType, nullable=True)

class Plants:
    def __init__(self, index):
        self.plant_name=""
        self.plant_birthday= datetime.today()
        self.plant_days_to_water =0
        self.is_dry= True
    def __repr__(self):
        return self.plant_name


@app.route('/')
def main():
    return render_template('index.html')




@app.route('/home/<user>')
def home(user):
    curr_user = User.query.filter_by(email=user).first()
    return render_template('index-signed.html',curr_user=curr_user)



@app.route('/showSignIn',methods=['POST','GET'])
def showSignIn():
    if request.method == 'POST':
        new_email = request.form['inputEmail']
        new_password = request.form['inputPassword']

        get_user = User.query.filter_by(email=new_email).first()

        if not get_user: # no user in DB
            message="Wrong email"
            return render_template('signin.html', message=message)
        else: #email  exists
            if not get_user.password == new_password:
                message="Wrong Password"
                return render_template('signin.html', message=message)
            else: #all valid
                curr_user = User.query.get(new_email)
                return redirect('/home/%s'%new_email)
    else:
        return render_template('signin.html')



@app.route('/showSignUp',methods=['POST','GET'])
def showSignUp():
    if request.method == 'POST':
        new_name = request.form['inputName']
        new_email = request.form['inputEmail']
        new_password = request.form['inputPassword']

        old_user = User.query.filter_by(email=new_email).first()
        if not old_user: # no user in DB
            new_user= User(name=new_name, email=new_email, password=new_password, plants_list={}, user_events=[])
            try:
                db.session.add(new_user)
                db.session.commit()

                return redirect('/home/%s'%new_email)

            except Exception as e:
                return json.dumps({'error':str(e)})

        else: #email already signed in
            message="Email Already registered"
            return render_template('signup.html', message=message)
    else:
        return render_template('signup.html')





@app.route('/addPlant/<user>',methods=['POST'])
def addPlant(user):
    curr_user = User.query.filter_by(email=user).first()
    index= len(curr_user.plants_list) + 1
    new_plant=Plants(index)
    if 'monestera' in request.form:
        new_plant.plant_name="monestera"
        new_plant.plant_days_to_water=10

    elif 'calathea' in request.form:
        new_plant.plant_name="calathea"
        new_plant.plant_days_to_water=20

    elif 'succulent' in request.form:
        new_plant.plant_name="succulent"
        new_plant.plant_days_to_water=30

    elif 'orchid' in request.form:
        new_plant.plant_name="orchid"
        new_plant.plant_days_to_water=30

    elif 'fotus/nanuk' in request.form:
        new_plant.plant_name="fotus/nanuk"
        new_plant.plant_days_to_water=7

    else:
        return json.dumps({'error':str(request.form)})

    update_list= curr_user.plants_list
    update_list.update({index: new_plant})
    upd_events=curr_user.user_events
    upd_events.append(add_event(new_plant, index))
    User.query.filter_by(email=user).update({"plants_list": update_list})
    User.query.filter_by(email=user).update({"user_events": upd_events})

    try:
        db.session.flush()
        db.session.commit()
        return redirect(request.referrer+'#addplant_garden')

    except Exception as e:
        return json.dumps({'error':str(e)})


def add_event(plant, id):
    event_made=Event()
    event_made.which_plant=plant.plant_name
    event_made.plant_id = id
    event_made.visited= "False"
    if not plant.is_dry==None:
        if plant.is_dry== 'yes':
            if 5<= datetime.today().month <= 9: #summer
                event_made.date=event_made.date+timedelta(days=plant.plant_days_to_water)
            else:
                event_made.date=event_made.date+timedelta(days=(plant.plant_days_to_water)*2)
        elif plant.is_dry== 'no':
            event_made.date=event_made.date+timedelta(days=2)
    return event_made


@app.route('/eventdry/<user>/<index>', methods=['POST'])
def eventdry(user, index):
    curr_user = User.query.filter_by(email=user).first()
    upd_plnt=curr_user.plants_list.get(int(index))
    upd_plnt.is_dry =request.form['is_dry'] #True or false
    curr_user.plants_list.update({int(index):upd_plnt})
    for event in curr_user.user_events:
        if event.plant_id == int(index):
            event.visited = 'True'
    curr_user.user_events.append(add_event(upd_plnt, int(index)))
    User.query.filter_by(email=user).update({"plants_list": curr_user.plants_list})
    User.query.filter_by(email=user).update({"user_events": curr_user.user_events})
    try:
        db.session.flush()
        db.session.commit()
        return redirect(request.referrer+'#calendar-title')

    except Exception as e:
        return json.dumps({'error':str(e)})





@app.route('/nickname/<user>/<index>',methods=['POST'])
def nickname(user, index):
    curr_user = User.query.filter_by(email=user).first()
    upd_plant = curr_user.plants_list.get(int(index))
    upd_plant.plant_name = request.form['new_plant_name']
    curr_user.plants_list.update({int(index) : upd_plant})

    for event in curr_user.user_events:
        if event.plant_id == int(index):
            event.which_plant= request.form['new_plant_name']
    User.query.filter_by(email=user).update({"plants_list": curr_user.plants_list})
    User.query.filter_by(email=user).update({"user_events": curr_user.user_events})
    try:
        db.session.flush()
        db.session.commit()
        return redirect(request.referrer+'#myGarden')
    except Exception as e:
        return json.dumps({'error':str(e)})


@app.route('/remove/<user>/<index>',methods=['POST'])
def remove(user, index):
    curr_user = User.query.filter_by(email=user).first()
    upd_event=[]
    for key in curr_user.plants_list:
        if key > int(index):
            curr_user.plants_list[key-1] = curr_user.plants_list.get(key)

    for event in curr_user.user_events:
        if event.plant_id < int(index):
            upd_event.append(event)
        elif event.plant_id > int(index):
            event.plant_id -=1
            upd_event.append(event)

    del curr_user.plants_list[len(curr_user.plants_list)]
    User.query.filter_by(email=user).update({"plants_list": curr_user.plants_list})
    User.query.filter_by(email=user).update({"user_events": upd_event})
    try:
        db.session.flush()
        db.session.commit()
        return redirect(request.referrer)

    except Exception as e:
        return json.dumps({'error':str(e)})
