from flask import Flask, render_template, redirect, url_for,request,flash

# from flask_wtf import FlaskForm 
# from wtforms import StringField, PasswordField, BooleanField,IntegerField,DateTimeField,SelectField,TextAreaField
# from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///login.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    timestamp=db.Column(db.DateTime,nullable=False,default=datetime.utcnow)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ssid=db.Column(db.String(20),unique=True)
    name = db.Column(db.String(20))
    age = db.Column(db.Integer)
    timestamp=db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    typeofbed = db.Column(db.String(20))
    address=db.Column(db.String(100))
    state=db.Column(db.String(40))
    city=db.Column(db.String(40))
    status=db.Column(db.Boolean,nullable=False,default=True)
    

    def __init__(self,ssid,name,age,timestamp,typeofbed,address,state,city):
        self.ssid=ssid
        self.name=name
        self.age=age
        self.timestamp=datetime(*[int(v) for v in timestamp.replace('T', '-').replace(':', '-').split('-')])
        self.typeofbed=typeofbed
        self.address=address
        self.state=state
        self.city=city

class Medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    medicinename = db.Column(db.String(30))
    quantity = db.Column(db.Integer)
    rate = db.Column(db.Integer)
    amount = db.Column(db.Integer)
    patient_id=db.Column(db.Integer)
    def __init__(self,name,quantity,rate,amount,patient_id):
        self.medicinename=name
        self.quantity=quantity
        self.rate=rate
        self.amount=amount
        self.patient_id=patient_id

class Diagnostics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    amount = db.Column(db.Integer)
    patient_id=db.Column(db.Integer)
    def __init__(self,name,amount,patient_id):
        self.name=name
        self.amount=amount
        self.patient_id=patient_id



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/insert',methods=["POST"])
@login_required
def insert():
    if request.method=="POST":
        ssid=request.form["ssid"]
        name=request.form["name"]
        age=request.form["age"]
        doj=request.form["doj"]
        typeofbed=request.form["typeofbed"]
        address=request.form["address"]
        state=request.form["state"]
        city=request.form["city"]
        patient=Patient(ssid,name,age,doj,typeofbed,address,state,city)
        db.session.add(patient)
        db.session.commit()
        flash("Patient Added Successfully!")
        return redirect(url_for('desk'))

@app.route('/insert2',methods=["POST"])
@login_required
def insert2():
    if request.method=="POST":
        medicinename=request.form["medicinename"]
        patient_id=request.form["patient_id"]
        quantity=request.form["quantity"]
        rate=request.form["rate"]
        amount=int(rate)*int(quantity)
        patient=Medicine(medicinename,quantity,rate,amount,patient_id)
        db.session.add(patient)
        db.session.commit()
        flash("Medicine Added Successfully!")
        return redirect(url_for('pharmacist'))

@app.route('/insert3',methods=["POST"])
@login_required
def insert3():
    if request.method=="POST":
        name=request.form["name"]
        patient_id=request.form["patient_id"]
        quantity=request.form["amount"]
        Diagnostic=Diagnostics(name,quantity,patient_id)
        db.session.add(Diagnostic)
        db.session.commit()
        flash("Diagnostics Added Successfully!")
        return redirect(url_for('diagnostic'))

@app.route('/report',methods=["POST","GET"])
@login_required
def report():
    if(current_user.username=="desk"):
        data=[]
        data1=[]
        data2=[]
        roomtype={"General Ward":2000,"Semi Sharing":4000,"Single Room":8000}
        amount=0
        if request.method=="POST":
            data1=Patient.query.filter(Patient.ssid.like("%"+request.form["searchtext"]+"%"),Patient.status==True )
            if data1.count()!=0:
                amount=amount+roomtype[data1[0].typeofbed]*int(str(datetime.utcnow() - data1[0].timestamp).split()[0])
                data=Medicine.query.filter(Medicine.patient_id.like("%"+str(data1[0].ssid)+"%"))
                for i in data:
                    amount=amount+i.amount
       
                data2=Diagnostics.query.filter(Diagnostics.patient_id.like("%"+str(data1[0].ssid)+"%"))
                for i in data2:
                    amount=amount+i.amount

        return render_template('dashboard4.html',data=data,data1=data1,data2=data2,amount=amount)
    else:
        return "<h2>Permission Denied<h2>"

@app.route('/delete/<int:id>',methods=["GET","POST"])
@login_required
def delete(id):
    data=Patient.query.get(id)
    db.session.delete(data)
    db.session.commit()
    flash("Patient Deleted Successfully!")
    return redirect(url_for("pharmacist"))

@app.route('/update/',methods=["POST","GET"])
@login_required
def update():
    if request.method=="POST":
        data=Patient.query.get(request.form["id"])
        data.ssid=request.form["ssid"]
        data.name=request.form["name"]
        data.age=request.form["age"]
        data.timestamp=datetime(*[int(v) for v in request.form["doj"].replace('T', '-').replace(':', '-').split('-')])
        data.typeofbed=request.form["typeofbed"]
        data.address=request.form["address"]
        data.state=request.form["state"]
        data.city=request.form["city"]
        db.session.commit()
        flash("Patient Details updated successfully!")
        return redirect(url_for('desk'))

@app.route('/update2/<int:id>',methods=["GET"])
@login_required
def update2(id):
    
    if request.method=="GET":
        data=Patient.query.get(id)
        data.status=False
        db.session.commit()
        flash("Patient is Discharged!")
        return redirect(url_for("report"))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=="POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user:
            if check_password_hash(user.password, request.form["password"]):
                print(request.form.get("checkbox"))
                login_user(user,remember=True if request.form.get("checkbox")=="on" else False)
                print(current_user)
                if(current_user.username=="desk"):
                    return redirect(url_for('desk'))
                elif(current_user.username=="pharmacist"):
                    return redirect(url_for('pharmacist'))
                elif(current_user.username=="diagnostic"):
                    return redirect(url_for('diagnostic'))
                    
        return '<h1>Invalid username or password</h1>'
    return render_template('login.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method=="POST":
        email=request.form["email"]
        username=request.form["username"]
        hashed_password = generate_password_hash(request.form["password"], method='sha256')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return '<h1>New user has been created!</h1>'
        #return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'
    else:
        return render_template('signup.html')

@app.route('/desk',methods=["GET","POST"])
@login_required
def desk():
    if(current_user.username=="desk"):
        data=[]
        if request.method=="POST":
            data=Patient.query.filter(Patient.ssid.like("%"+request.form["searchtext"]+"%"),Patient.status==True)
        else :
            data=Patient.query.all()
        # print(data[0].timestamp)
        return render_template('dashboard.html',data=data, name=current_user.username)
    else:
        return "<h2>Permission Denied<h2>"



@app.route('/pharmacist',methods=["GET","POST"])
@login_required
def pharmacist():
    if(current_user.username=="pharmacist" or current_user.username=="desk" ):
        data=[]
        data1=[]
        if request.method=="POST":
            data1=Patient.query.filter(Patient.ssid.like("%"+request.form["searchtext"]+"%"),Patient.status==True)
            if data1.count()!=0:
                data=Medicine.query.filter(Medicine.patient_id.like("%"+str(data1[0].ssid)+"%"))
        else:
            data=Medicine.query.all()
            data1=Patient.query.filter(Patient.status==True)
        return render_template('dashboard2.html',data=data, data1=data1,name=current_user.username)
    else:
        return "<h2>Permission Denied<h2>"


@app.route('/diagnostic',methods=["GET","POST"])
@login_required
def diagnostic():
    if(current_user.username=="diagnostic" or current_user.username=="desk" ):
        data=[]
        data1=[]
        if request.method=="POST":
            data1=Patient.query.filter(Patient.ssid.like("%"+request.form["searchtext"]+"%"),Patient.status==True)
            if data1.count()!=0:
                data=Diagnostics.query.filter(Diagnostics.patient_id.like("%"+str(data1[0].ssid)+"%"))
        else:
            data1=Patient.query.filter(Patient.status==True)
            data=Diagnostics.query.all()
        return render_template('dashboard3.html',data=data, data1=data1,name=current_user.username)

    else:
        return "<h2>Permission Denied<h2>"




@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
