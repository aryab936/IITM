from flask import Flask, request,jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime
from flask_restful import Api, Resource,reqparse,abort
from flask_cors import CORS
import functools
import jwt
import celery
from celery import Celery
from celery.schedules import crontab
import httplib2
import json
from datetime import date
from flask_caching import Cache
from sendingEmails import send_email
import os

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///test.db?charset=utf8'

db=SQLAlchemy(app)
app.config['SECRET_KEY'] = "VerySecretiveIndeed"
api = Api(app)
app.config.from_object(__name__)



CORS(app)
celery1 = Celery("app")
class MyCeleryTasks(celery1.Task):
	def __call__(self,*args,**kwargs):
		with app.app_context():
			return self.run(*args,**kwargs)
celery1.conf.update(broker_url = "redis://localhost:6379/1",result_backend="redis://localhost:6379/2", result_expires = 60)
celery1.Task =MyCeleryTasks


cache = Cache(config={'CACHE_TYPE': 'RedisCache'})
cache.init_app(app)

#Starting to define the Database
class User(db.Model):
	__tablename__ = 'user'
	user_id=db.Column(db.Integer,primary_key=True, nullable = False)
	user_name=db.Column(db.String(100),nullable=False, unique = True)
	first_name=db.Column(db.String(100), nullable=False)
	last_name=db.Column(db.String(100))
	password=db.Column(db.String(100),nullable=False)
	email = db.Column(db.String(100), unique = True, nullable = False)
	url = db.Column(db.String(400), nullable = False)  

class Tracker(db.Model):
	__tablename__ = 'tracker'
	tracker_id=db.Column(db.Integer, primary_key=True)
	user_id=db.Column(db.Integer,db.ForeignKey('user.user_id'),primary_key = True, nullable=False)
	tracker_type=db.Column(db.String(100), nullable=False)
	tracker_name=db.Column(db.String(100),nullable=False)
	description=db.Column(db.String(100),nullable=False)
	tracker_last_reviewed=db.Column(db.DateTime,default=datetime.datetime.utcnow(), nullable=True)
	tracker_last_logged=db.Column(db.DateTime,default=datetime.datetime.utcnow(), nullable=True)

class Tracker_Numerical(db.Model):
	tracker_id=db.Column(db.Integer,db.ForeignKey('tracker.tracker_id'), nullable=False, primary_key=True)
	user_id=db.Column(db.Integer,db.ForeignKey('user.user_id'), nullable=False, primary_key=True)
	tracker_timestamp=db.Column(db.DateTime,default=datetime.datetime.utcnow())
	tracker_value=db.Column(db.Float,nullable=False)
	tracker_note=db.Column(db.String(100))
	tracker_log_id=db.Column(db.Integer,nullable = False, primary_key = True) 
	

class Tracker_multi_choice(db.Model):
	tracker_id=db.Column(db.Integer,db.ForeignKey('tracker.tracker_id'), nullable=False, primary_key=True)
	user_id=db.Column(db.Integer,db.ForeignKey('user.user_id'), nullable=False, primary_key=True)
	tracker_timestamp=db.Column(db.DateTime,default=datetime.datetime.utcnow(),primary_key=True)
	tracker_value=db.Column(db.String(50),nullable=False)
	tracker_note=db.Column(db.String(100))
	tracker_log_id=db.Column(db.Integer,nullable = False, primary_key = True) 

class Tracker_boolean(db.Model):
	tracker_id=db.Column(db.Integer,db.ForeignKey('tracker.tracker_id'), nullable=False, primary_key=True)
	user_id=db.Column(db.Integer,db.ForeignKey('user.user_id'), nullable=False, primary_key=True)
	tracker_timestamp=db.Column(db.DateTime,default=datetime.datetime.utcnow(), primary_key=True)
	tracker_value=db.Column(db.Boolean,nullable=False)
	tracker_note=db.Column(db.String(100))
	tracker_log_id=db.Column(db.Integer,nullable = False, primary_key = True) 

class Tracker_time_duration(db.Model):
	tracker_id=db.Column(db.Integer,db.ForeignKey('tracker.tracker_id'), nullable=False, primary_key=True)
	user_id=db.Column(db.Integer,db.ForeignKey('user.user_id'), nullable=False, primary_key=True)
	tracker_timestamp=db.Column(db.DateTime,default=datetime.datetime.utcnow(), nullable = False, unique = True)
	tracker_hours=db.Column(db.Integer,nullable=False)
	tracker_minutes=db.Column(db.Integer,nullable=False)
	tracker_note=db.Column(db.String(100))
	tracker_log_id=db.Column(db.Integer,nullable = False, primary_key = True) 

class Tracker_options_multi(db.Model):
	tracker_id=db.Column(db.Integer,db.ForeignKey('tracker.tracker_id'), nullable=False, primary_key=True)
	user_id=db.Column(db.Integer,db.ForeignKey('user.user_id'), nullable=False, primary_key=True)
	option=db.Column(db.String(100), nullable=False, primary_key=True)

#Database Definition Ends Here

#JWT Code

def authtoken_required(function):
	@functools.wraps(function)
	def loggedin(*args,**kwargs):
		auth_token=None
		try:
			auth_token = request.headers['secret_authtoken']
		
		except:
			return jsonify({"status":'unsuccessful, missing the authtoken'})
		
		try: 
			output = jwt.decode(auth_token,app.config['SECRET_KEY'])
			#print(output)
			user = User.query.filter_by(user_id = output["user_id"]).first()
		except:
			return jsonify({"status":"failure, your token details do not match"})
		
		return function(*args,user.user_id,**kwargs)
	return loggedin


#Defining Auxilliary functions for login resource

@celery1.task()
def export_dashboard(user_id):
	records = list(Tracker.query.filter_by(user_id = user_id).all())
	with open(r"dashboard_"+str(user_id)+".csv","w") as f:
		f.write("Tracker ID,Tracker Type,Tracker Name,Tracker Description,Tracker Last Reviewed Timestamp,Tracker Last Logged Timestamp\n")
		records = list(records)
		for item in records:
			last_reviewed=str(item.tracker_last_reviewed)
			last_logged=str(item.tracker_last_logged)
			thing = "{tracker_id},{tracker_type},{tracker_name},{description},{reviewed},{logged}\n"
			f.write(thing.format(tracker_id = item.tracker_id,tracker_type = item.tracker_type, tracker_name = item.tracker_name, description = item.description, reviewed =last_reviewed, logged = last_logged))
			f.flush()
		f.close()
	filename = "dashboard_"+str(user_id)+".csv"
	user = User.query.filter_by(user_id = user_id).first()
	email_address = str(user.email)
	send_email(email_address,"Status of your Download","Your download has been successfully completed. You can find your download attached in this email.",filename)
	os.remove(filename)

@celery1.task()
def export_logs_numerical(user_id, tracker_id):
	records = Tracker_Numerical.query.filter_by(user_id = user_id, tracker_id = tracker_id).all()
	records = list(records)
	user = User.query.filter_by(user_id = user_id).first()
	email_address = str(user.email)
	if len(records) ==0:
		send_email(email_address,"Status of your Download","The tracker id you specified may not exist or may not contain any records and therefore we have not attached the CSV file.")
		return 
	with open(r"numerical_"+str(user_id)+str(tracker_id)+".csv","w") as f:
		f.write("Tracker Value,Tracker Timestamp,Tracker Notes\n")
		for item in records:
			timestamp = str(item.tracker_timestamp)
			thing = "{value},{timestamp},{note}\n"
			f.write(thing.format(value = item.tracker_value,timestamp = timestamp, note = item.tracker_note))
			f.flush()
		f.close()
	filename = "numerical_"+str(user_id)+str(tracker_id)+".csv"
	send_email(email_address,"Status of your Download","Your download has been successfully completed. You can find your download attached in this email.",filename)
	os.remove(filename)
    
@celery1.task()
def export_logs_time_duration(user_id, tracker_id):
	records = Tracker_time_duration.query.filter_by(user_id = user_id, tracker_id = tracker_id).all()
	records = list(records)
	user = User.query.filter_by(user_id = user_id).first()
	email_address = str(user.email)
	if len(records) ==0:
		send_email(email_address,"Status of your Download","The tracker id you specified may not exist or may not contain any records and therefore we have not attached the CSV file.")
		return 
	with open(r"time_duration"+str(user_id)+str(tracker_id)+".csv","w") as f:
		f.write("Tracker Hours,Tracker Minutes,Tracker Timestamp,Tracker Notes\n")
		for item in records:
			thing = "{hours},{minutes},{timest},{notes}\n"
			f.write(thing.format(hours = item.tracker_hours,minutes = item.tracker_minutes,timest=item.tracker_timestamp,notes= item.tracker_note))
			f.flush()
		f.close()
	filename = "time_duration"+str(user_id)+str(tracker_id)+".csv"
	send_email(email_address,"Status of your Download","Your download has been successfully completed. You can find your download attached in this email.",filename)
	os.remove(filename)

@celery1.task()
def export_logs_boolean(user_id, tracker_id):
	records = Tracker_boolean.query.filter_by(user_id = user_id, tracker_id = tracker_id).all()
	records = list(records)
	user = User.query.filter_by(user_id = user_id).first()
	email_address = str(user.email)
	if len(records) ==0:
		send_email(email_address,"Status of your Download","The tracker id you specified may not exist or may not contain any records and therefore we have not attached the CSV file.")
		return 
	with open(r"boolean_"+str(user_id)+str(tracker_id)+".csv","w") as f:
		f.write("Tracker Value,Tracker Timestamp,Tracker Notes\n")
		for item in records:
			timestamp = str(item.tracker_timestamp)
			thing = "{value},{timestamp},{note}\n"
			f.write(thing.format(value = item.tracker_value,timestamp = timestamp, note = item.tracker_note))
			f.flush()
		f.close()
	filename = "boolean_"+str(user_id)+str(tracker_id)+".csv"
	send_email(email_address,"Status of your Download","Your download has been successfully completed. You can find your download attached in this email.",filename)
	os.remove(filename)

@celery1.task()
def export_logs_multichoice(user_id,tracker_id):
	records = Tracker_multi_choice.query.filter_by(user_id = user_id, tracker_id = tracker_id).all()
	records = list(records)
	user = User.query.filter_by(user_id = user_id).first()
	email_address = str(user.email)
	if len(records) ==0:
		send_email(email_address,"Status of your Download","The tracker id you specified may not exist or may not contain any records and therefore we have not attached the CSV file.")
		return 
	with open(r"multichoice_"+str(user_id)+str(tracker_id)+".csv","w") as f:
		f.write("Tracker Value,Tracker Timestamp,Tracker Notes\n")
		for item in records:
			timestamp = str(item.tracker_timestamp)
			thing = "{value},{timestamp},{note}\n"
			f.write(thing.format(value = item.tracker_value,timestamp = timestamp, note = item.tracker_note))
			f.flush()
		f.close()
	filename = "multichoice_"+str(user_id)+str(tracker_id)+".csv"
	send_email(email_address,"Status of your Download","Your download has been successfully completed. You can find your download attached in this email.",filename)
	os.remove(filename)



#Creating a resource for login 

class Login(Resource):
	def post(self):
		args = request.get_json(force=True)
		#print(args)
		user = User.query.filter_by(user_name = args["username"], password = args["password"]).first()
		if not user:
			abort(403, message= "The credentials do not match!")
		else:
				authtoken = jwt.encode({"user_id":user.user_id,'exp' : datetime.datetime.utcnow()+datetime.timedelta(minutes = 300)},app.config['SECRET_KEY'])
				thing = {"status":"success","authtoken":authtoken.decode('UTF-8')}
				return jsonify(thing)
				

api.add_resource(Login,"/login")


#Defining some auxilliary functions for the Numerical Trackers Logs API

@cache.memoize(60)
def get_helper_numerical(user_id,id):
	records = Tracker_Numerical.query.filter_by(user_id=user_id,tracker_id=id).all()
	if records:
		l=[]
		records=list(records)
		for record in records:
			d={}
			d["user_id"] = record.user_id 
			d["tracker_id"] = record.tracker_id
			d["timestamp"] =record.tracker_timestamp
			d["value"] = record.tracker_value
			d["note"] = record.tracker_note
			d["logID"] = record.tracker_log_id
			l.append(d)
		data = {"data":l,"status":"success"}
		return jsonify(data)
	else:
		abort(404,message="The tracker record you requested doesn't exist or has no logs!")

#Defining resources for Numerical Tracker Logs

class NumericalLog(Resource):
	logID = 1
	@authtoken_required
	def get(self,user_id,id):
		#print("Inside Get")
		#print(user_id)
		#print(id)
		return get_helper_numerical(user_id,id)
		
	@authtoken_required
	def post(self,user_id,id):
		user = User.query.filter_by(user_id=user_id).first()
		tracker=Tracker.query.filter_by(user_id = user_id,tracker_id=id, tracker_type = "Numerical").first()
		if user and tracker:
			#print("Over here!")
			time = datetime.datetime.utcnow()
			args = request.get_json(force = True)
			#print(args)
			record = Tracker_Numerical.query.filter_by(tracker_id = id, user_id = user_id, tracker_log_id = NumericalLog.logID).first()
			try:
				a = args["value"]
				b = args["note"]
			except:
				abort(404, message= "Some of the mandatory fields are missing in request body.")
			flag = ""
			if record:
				flag = True
			else:
				flag = False
			while flag:
					record = Tracker_Numerical.query.filter_by(tracker_id = id, user_id = user_id, tracker_log_id = NumericalLog.logID).first()
					if record:
						flag = True
						NumericalLog.logID+=1
					else:
						flag =False
			
				#print("Reached here!")
			try:
				newlog = Tracker_Numerical(tracker_id = id,user_id=user_id,tracker_timestamp= time,tracker_value = a,tracker_note = b,tracker_log_id=NumericalLog.logID)
				NumericalLog.logID+=1
				db.session.commit()
				db.session.add(newlog)
				tracker.tracker_last_logged = datetime.datetime.utcnow()
				db.session.commit()
				cache.delete_memoized(get_helper_numerical)
				return jsonify({"status":"success"})
			except:
				return jsonify({"status":"failed","message":"Please enter a numerical value only."})
		else:
			abort(404,message="Either the user doesn't exist or the tracker doesn't exist!")
	
	@authtoken_required
	def patch(self,user_id,id):
		user = User.query.filter_by(user_id=user_id).first()
		tracker=Tracker.query.filter_by(user_id = user_id,tracker_id=id, tracker_type = "Numerical").first()
		if user and tracker:
			args = request.get_json(force = True)
			try:
				record = Tracker_Numerical.query.filter_by(tracker_id = id, user_id = user_id, tracker_log_id = args["logID"]).first()
				if record:
					if (args["value"]):
						try:
							record.tracker_value = int(args["value"])
						except:
							return jsonify({"status":"failed","message":"Please enter a numerical value only."})
					if args["note"]:
						record.tracker_note = args["note"]
					if args["timestamp"]:
						#print("Inside path timestamp")
						record.tracker_timestamp = datetime.datetime.strptime(args["timestamp"],'%Y-%m-%d %H:%M:%S.%f')
					tracker.tracker_last_reviewed = datetime.datetime.utcnow()
					cache.delete_memoized(get_helper_numerical)				
					db.session.commit()
					return jsonify({"status":"success"})
				else:
					abort(404,message = "The log with specified ID doesn't exist for the tracker")
			except:
				abort(404,message="Either some mandatory fields are missing in request body or log doesn't exist.")
		else:
			abort(404,message = "Either the user doesn't exist or the tracker doesn't exist")


class DeleteNumerical(Resource):
	@authtoken_required
	def delete(self,user_id,id,logID):
			user = User.query.filter_by(user_id=user_id).first()
			tracker=Tracker.query.filter_by(user_id = user_id,tracker_id=id, tracker_type = "Numerical").first()
			if user and tracker:
				record = Tracker_Numerical.query.filter_by(tracker_id = id, user_id = user_id , tracker_log_id = logID).first()
				if record:
					db.session.delete(record)
					db.session.commit()
					cache.delete_memoized(get_helper_numerical)	
					return jsonify({"status":"success"})
				else:
					abort(404,message="The record you have specified already doesn't exist.")
			else:
					abort(404,message="Either the user doesn't exist or the tracker doesn't exist.")

class downloadNumerical(Resource):
	@authtoken_required
	def get(self,user_id,tracker_id):
		#print("Tracker ID")
		#print(tracker_id)
		export_logs_numerical.delay(user_id,tracker_id)

api.add_resource(NumericalLog,"/numericLogs/<int:id>")

api.add_resource(DeleteNumerical,"/numericLogs/<int:id>/<int:logID>")

api.add_resource(downloadNumerical,"/downloadNumeric/<int:tracker_id>")


#Defining some auxilliary functions for the Boolean Trackers' Logs API

def str2bool(string):
	if string.lower() == "true":
		return True
	else:
		return False

@cache.memoize(60)
def get_helper_boolean(user_id,id):
	records = Tracker_boolean.query.filter_by(user_id=user_id,tracker_id=id).all()
	if records:
		l=[]
		records=list(records)
		for record in records:
			d={}
			d["user_id"] = record.user_id 
			d["tracker_id"] = record.tracker_id
			d["timestamp"] = record.tracker_timestamp
			d["value"] = record.tracker_value
			d["note"] = record.tracker_note
			d["logID"] = record.tracker_log_id
			l.append(d)
		data = {"data":l,"status":"success"}
		return jsonify(data)
	else:
		abort(404,message="The tracker record you requested doesn't exist or has no logs!")

#Defining resources for Boolean Tracker Logs

class BooleanLog(Resource):
	logID = 1
	@authtoken_required
	
	def get(self,user_id,id):
		#print("Inside Get")
		#print(user_id)
		#print(id)
		return get_helper_boolean(user_id,id)
	
	@authtoken_required
	def post(self,user_id,id):
		user = User.query.filter_by(user_id=user_id).first()
		tracker=Tracker.query.filter_by(user_id = user_id,tracker_id=id, tracker_type = "Boolean").first()
		if user and tracker:
			#print("Over here!")
			time = datetime.datetime.utcnow()
			args = request.get_json(force = True)
			#print(args)
			record = Tracker_boolean.query.filter_by(tracker_id = id, user_id = user_id, tracker_log_id = BooleanLog.logID).first()
			flag = ""
			if record:
				flag = True
			else:
				flag = False
			
			while flag:
				record = Tracker_boolean.query.filter_by(tracker_id = id, user_id = user_id, tracker_log_id = BooleanLog.logID).first()
				if record:
					flag = True
					BooleanLog.logID+=1
				else:
					flag = False
			
				#print("Reached here!")
			try:
				newlog = Tracker_boolean(tracker_id = id,user_id=user_id,tracker_timestamp= time,tracker_value = args["value"],tracker_note = args["note"],tracker_log_id=BooleanLog.logID)
				BooleanLog.logID+=1
				db.session.commit()
				db.session.add(newlog)
				tracker.tracker_last_logged = datetime.datetime.utcnow()
				db.session.commit()
				cache.delete_memoized(get_helper_boolean)
				return jsonify({"status":"success"})
			except:
				abort(404,message="Some of the mandatory values are missing.")
		else:
			abort(404,message="Either the user doesn't exist or the tracker doesn't exist!")
	
	@authtoken_required
	def patch(self,user_id,id):
		user = User.query.filter_by(user_id=user_id).first()
		tracker=Tracker.query.filter_by(user_id = user_id,tracker_id=id, tracker_type = "Boolean").first()
		if user and tracker:
			args = request.get_json(force = True)
			try:
				record = Tracker_boolean.query.filter_by(tracker_id = id, user_id = user_id, tracker_log_id = args["logID"]).first()
				if record is not None:
						if (args["value"] is not None and len(str(args["value"]))>0):
							print(type(args["value"]))
							print(args["value"])
							record.tracker_value =args["value"]
						if args["note"]:
							record.tracker_note = args["note"]
						if args["timestamp"]:
							#print("Inside path timestamp")
							record.tracker_timestamp = datetime.datetime.strptime(args["timestamp"],'%Y-%m-%d %H:%M:%S.%f')
						tracker.tracker_last_reviewed = datetime.datetime.utcnow()
						db.session.commit()
						cache.delete_memoized(get_helper_boolean)
						return jsonify({"status":"success"})
				else:
					abort(404,message = "The log with specified ID doesn't exist for the tracker")
			except:
				abort(404, message= "Some of the mandatory fields are missing or the log doesn't exist for the provided logID.")
			
		else:
			abort(404,message = "Either the user doesn't exist or the tracker doesn't exist")

class DeleteBoolean(Resource):

	@authtoken_required
	def delete(self,user_id,id,logID):
			user = User.query.filter_by(user_id=user_id).first()
			tracker=Tracker.query.filter_by(user_id = user_id,tracker_id=id, tracker_type = "Boolean").first()
			if user and tracker:
				record = Tracker_boolean.query.filter_by(tracker_id = id, user_id = user_id , tracker_log_id = logID).first()
				if record:
					db.session.delete(record)
					db.session.commit()
					cache.delete_memoized(get_helper_boolean)
					return jsonify({"status":"success"})
				else:
					abort(404,message="The record you have specified already doesn't exist.")
			else:
					abort(404,message="Either the user doesn't exist or the tracker doesn't exist.")	

class downloadBoolean(Resource):
	@authtoken_required
	def get(self,user_id,tracker_id):
		#print("Tracker ID")
		#print(tracker_id)
		export_logs_boolean.delay(user_id,tracker_id)

api.add_resource(BooleanLog,"/booleanLogs/<int:id>")

api.add_resource(DeleteBoolean,"/booleanLogs/<int:id>/<int:logID>")

api.add_resource(downloadBoolean,"/downloadBoolean/<int:tracker_id>")

#Defining some auxilliary functions for the TimeDuration Trackers' Logs API

@cache.memoize(60)
def get_helper_time_duration(user_id,id):
	records = Tracker_time_duration.query.filter_by(user_id=user_id,tracker_id=id).all()
	if records:
		l=[]
		records=list(records)
		for record in records:
			d={}
			d["user_id"] = record.user_id 
			d["tracker_id"] = record.tracker_id
			d["timestamp"] =record.tracker_timestamp
			d["hours"] = record.tracker_hours
			d["minutes"] = record.tracker_minutes
			d["note"] = record.tracker_note
			d["logID"] = record.tracker_log_id
			l.append(d)
		data = {"data":l,"status":"success"}
		return jsonify(data)
	else:
		abort(404,message="The tracker record you requested doesn't exist or has no logs!")



#Defining resources for Time Duration Tracker Logs

class TimeDurationLog(Resource):
	logID = 1
	@authtoken_required
	
	def get(self,user_id,id):
		#print("Inside Get")
		#print(user_id)
		#print(id)
		return get_helper_time_duration(user_id,id)
	
	@authtoken_required
	def post(self,user_id,id):
		user = User.query.filter_by(user_id=user_id).first()
		tracker=Tracker.query.filter_by(user_id = user_id,tracker_id=id, tracker_type="Time Duration").first()
		print(tracker)
		if user and tracker:
				#print("Over here!")
				time = datetime.datetime.utcnow()
				args = request.get_json(force= True)
				#print(args)
				record = Tracker_time_duration.query.filter_by(tracker_id = id, user_id = user_id, tracker_log_id = TimeDurationLog.logID).first()
				flag = ""
				if record:
					flag = True
				else:
					flag = False
				
				while flag:
					record = Tracker_time_duration.query.filter_by(tracker_id = id, user_id = user_id, tracker_log_id = TimeDurationLog.logID).first()
					if record:
						flag = True
						TimeDurationLog.logID+=1
					else:
						flag = False
				
					#print("Reached here!")
				try:
					newlog = Tracker_time_duration(tracker_id = id,user_id=user_id,tracker_timestamp= time,tracker_hours= args["hours"],tracker_minutes = args["minutes"],tracker_note = args["note"],tracker_log_id=TimeDurationLog.logID)
					TimeDurationLog.logID+=1
					db.session.commit()
					db.session.add(newlog)
					tracker.tracker_last_logged = datetime.datetime.utcnow()
					db.session.commit()
					cache.delete_memoized(get_helper_time_duration)
					return jsonify({"status":"success"})
				except:
					abort(404,message="Some values which are mandatory fields are missing in the request body.")
		else:
			abort(404,message="Either the user doesn't exist or the tracker doesn't exist!")
	
	@authtoken_required
	def patch(self,user_id,id):
		user = User.query.filter_by(user_id=user_id).first()
		tracker=Tracker.query.filter_by(user_id = user_id,tracker_id=id, tracker_type="Time Duration").first()
		if user and tracker:
			args = request.get_json(force = True)
			record = Tracker_time_duration.query.filter_by(tracker_id = id, user_id = user_id, tracker_log_id = args["logID"]).first()
			if record:
				try:
					if (args["hours"]):
						record.tracker_hours = args["hours"]
					if (args["minutes"]):
						record.tracker_minutes = args["minutes"]
					if args["note"]:
						record.tracker_note = args["note"]
					if args["timestamp"]:
						#print("Inside path timestamp")
						record.tracker_timestamp = datetime.datetime.strptime(args["timestamp"],'%Y-%m-%d %H:%M:%S.%f')
					tracker.tracker_last_reviewed = datetime.datetime.utcnow()
					db.session.commit()
					cache.delete_memoized(get_helper_time_duration)
					return jsonify({"status":"success"})
				except:
					abort(404,message="If you wish to not change some field, leave it empty instead of removing it completely from the request body.")
			else:
				abort(404,message = "The log with specified ID doesn't exist for the tracker")
		else:
			abort(404,message = "Either the user doesn't exist or the tracker doesn't exist")

class DeleteTimeDuration(Resource):
	@authtoken_required
	def delete(self,user_id,id,logID):
			user = User.query.filter_by(user_id=user_id).first()
			tracker=Tracker.query.filter_by(user_id = user_id,tracker_id=id, tracker_type = "Time Duration").first()
			if user and tracker:
				record = Tracker_time_duration.query.filter_by(tracker_id = id, user_id = user_id , tracker_log_id = logID).first()
				if record:
					db.session.delete(record)
					db.session.commit()
					cache.delete_memoized(get_helper_time_duration)
					return jsonify({"status":"success"})
				else:
					abort(404,message="The record you have specified already doesn't exist.")
			else:
					abort(404,message="Either the user doesn't exist or the tracker doesn't exist.")

class downloadTimeDuration(Resource):
	@authtoken_required
	def get(self,user_id,tracker_id):
		#print("Tracker ID")
		#print(tracker_id)
		export_logs_time_duration.delay(user_id,tracker_id)

api.add_resource(TimeDurationLog,"/timeDurationLogs/<int:id>")

api.add_resource(DeleteTimeDuration,"/timeDurationLogs/<int:id>/<int:logID>")

api.add_resource(downloadTimeDuration,"/downloadTimeDuration/<int:tracker_id>")

#Defining some auxilliary functions for the MutliChoice Trackers' Options API

@cache.memoize(60)
def get_options_multi_helper(user_id,id):
	records = Tracker_options_multi.query.filter_by(user_id=user_id,tracker_id=id).all()
	if records:
		l=[]
		records=list(records)
		for record in records:
			d={}
			d["user_id"] = record.user_id 
			d["tracker_id"] = record.tracker_id
			d["option"] = record.option
			l.append(d)
		data = {"data":l,"status":"success"}
		return jsonify(data)
	else:
		abort(404,message="The tracker record you requested doesn't exist or has no logs!")

#Defining resources for Boolean Tracker Logs

class MultiChoiceOptions(Resource):
	
	@authtoken_required
	
	def get(self,user_id,id):
		#print("Inside Get")
		#print(user_id)
		#print(id)
		return get_options_multi_helper(user_id,id)
	
	@authtoken_required
	def post(self,user_id,id):
		user = User.query.filter_by(user_id=user_id).first()
		tracker=Tracker.query.filter_by(user_id = user_id,tracker_id=id, tracker_type = "Multi Choice").first()
		if user and tracker:
			#print("Over here!")
			args = request.get_json(force = True)
			if bool(args["options"]):
				if len(args["options"])>0:
					thing = args["options"].split(",")
			#print(args)
					for item in thing:
						record = Tracker_options_multi.query.filter_by(tracker_id = id, user_id = user_id, option=item).first()
						if record:
							abort(409,message="There is already an existing option!")
					
					for item in thing:
						newlog = Tracker_options_multi(tracker_id = id,user_id=user_id,option = item)
						db.session.commit()
						db.session.add(newlog)
						db.session.commit()
					cache.delete_memoized(get_options_multi_helper)
					return jsonify({"status":"success"})
				else:
					abc = jsonify({"status":"failure","message":"Please add atleast one option"})
					abc.status_code = 404
					return abc
			else:
				abc = jsonify({"status":"failure","message":"Please add atleast one option"})
				abc.status_code = 404
				return abc
			
			#print("Reached here!")
			
		else:
			abort(404,message="Either the user doesn't exist or the tracker doesn't exist!")


class DeleteOptionsMulti(Resource):
	
	@authtoken_required
	def delete(self,user_id,id,option):
			user = User.query.filter_by(user_id=user_id).first()
			tracker=Tracker.query.filter_by(user_id = user_id,tracker_id=id, tracker_type = "Multi Choice").first()
			if user and tracker:
				record = Tracker_options_multi.query.filter_by(tracker_id = id, user_id = user_id , option= option).first()
				if record:
					db.session.delete(record)
					db.session.commit()
					cache.delete_memoized(get_options_multi_helper)
					return jsonify({"status":"success"})
				else:
					abort(404,message="The option you have specified already doesn't exist.")
			else:
					abort(404,message="Either the user doesn't exist or the tracker doesn't exist.")	


api.add_resource(MultiChoiceOptions,"/optionsMulti/<int:id>")

api.add_resource(DeleteOptionsMulti,"/deleteOptions/<int:id>/<string:option>")


#Defining some auxilliary functions for the TimeDuration Trackers' Logs API

@cache.memoize(60)
def get_multichoice_records_helper(user_id,id):
	records = Tracker_multi_choice.query.filter_by(user_id=user_id,tracker_id=id).all()
	if records:
		l=[]
		records=list(records)
		for record in records:
			d={}
			d["user_id"] = record.user_id 
			d["tracker_id"] = record.tracker_id
			d["timestamp"] = record.tracker_timestamp
			d["value"] = record.tracker_value
			d["note"] = record.tracker_note
			d["logID"] = record.tracker_log_id
			l.append(d)
		data = {"data":l,"status":"success"}
		return jsonify(data)
	else:
		abort(404,message="The tracker record you requested doesn't exist or has no logs!")

#Defining resources for MultiChoice Tracker Logs

class MultiChoiceLog(Resource):
	logID = 1
	
	@authtoken_required
	
	def get(self,user_id,id):
		#print("Inside Get")
		#print(user_id)
		#print(id)
		return get_multichoice_records_helper(user_id,id)
	
	@authtoken_required
	def post(self,user_id,id):
		user = User.query.filter_by(user_id=user_id).first()
		tracker=Tracker.query.filter_by(user_id = user_id,tracker_id=id, tracker_type = "Multi Choice").first()
		if user and tracker:
			#print("Over here!")
			time = datetime.datetime.utcnow()
			args = request.get_json(force= True)
			#print(args)
			record = Tracker_multi_choice.query.filter_by(tracker_id = id, user_id = user_id, tracker_log_id = MultiChoiceLog.logID).first()
			flag = ""
			if record:
				flag = True
			else:
				flag = False
			
			while flag:
				record = Tracker_multi_choice.query.filter_by(tracker_id = id, user_id = user_id, tracker_log_id = MultiChoiceLog.logID).first()
				if record:
					flag = True
					MultiChoiceLog.logID+=1
				else:
					flag = False
			
				#print("Reached here!")
			try:
				value = args["value"]
				options = Tracker_options_multi.query.filter_by(tracker_id = id,user_id = user_id, option = value).all()
				if options:
					newlog = Tracker_multi_choice(tracker_id = id,user_id=user_id,tracker_timestamp= time,tracker_value = value,tracker_note = args["note"],tracker_log_id=MultiChoiceLog.logID)
					MultiChoiceLog.logID+=1
					db.session.commit()
					db.session.add(newlog)
					tracker.tracker_last_logged = datetime.datetime.utcnow()
					db.session.commit()
					cache.delete_memoized(get_multichoice_records_helper)
					return jsonify({"status":"success"})
				else:
					abc = jsonify({"status":"failure","message":"Failed: You have not entered a valid option. Please enter one to proceed."})
					abc.status_code = 404
					return abc
			except:
				abort(404,message="One or more required fields are missing.")
		else:
			abort(404,message="One or more required fields are missing; Alternatively,either the user doesn't exist or the tracker doesn't exist!")
	
	@authtoken_required
	def patch(self,user_id,id):
		user = User.query.filter_by(user_id=user_id).first()
		tracker=Tracker.query.filter_by(user_id = user_id,tracker_id=id, tracker_type = "Multi Choice").first()
		if user and tracker:
			args = request.get_json(force= True)
			record = Tracker_multi_choice.query.filter_by(tracker_id = id, user_id = user_id, tracker_log_id = args["logID"]).first()
			if record:
				try:
					if (args["value"]):
						value = args["value"]
						options = Tracker_options_multi.query.filter_by(tracker_id = id,user_id = user_id, option = value).all()
						if options:
							record.tracker_value = args["value"]
						else:
							abort(404, message ="Please enter a valid option")
					
					if args["note"]:
						record.tracker_note = args["note"]
					if args["timestamp"]:
						#print("Inside path timestamp")
						record.tracker_timestamp = datetime.datetime.strptime(args["timestamp"],'%Y-%m-%d %H:%M:%S.%f')
					tracker.tracker_last_reviewed = datetime.datetime.utcnow()
					cache.delete_memoized(get_multichoice_records_helper)
					db.session.commit()
					return jsonify({"status":"success"})
				except:
					abort(404,message ="Either one of the required fields is missing or the option value is not valid.")
			else:
				abort(404,message = "The log with specified ID doesn't exist for the tracker")
		else:
			abort(404,message = "Either the user doesn't exist or the tracker doesn't exist")

class DeleteMultiChoice(Resource):
	
	@authtoken_required
	def delete(self,user_id,id,logID):
			user = User.query.filter_by(user_id=user_id).first()
			tracker=Tracker.query.filter_by(user_id = user_id,tracker_id=id, tracker_type = "Multi Choice").first()
			if user and tracker:
				record = Tracker_multi_choice.query.filter_by(tracker_id = id, user_id = user_id , tracker_log_id = logID).first()
				if record:
					db.session.delete(record)
					db.session.commit()
					cache.delete_memoized(get_multichoice_records_helper)
					return jsonify({"status":"success"})
				else:
					abort(404,message="The record you have specified already doesn't exist.")
			else:
					abort(404,message="The tracker doesn't exist.")


class downloadMultiChoice(Resource):
	@authtoken_required
	def get(self,user_id,tracker_id):
		#print("Tracker ID")
		#print(tracker_id)
		export_logs_multichoice.delay(user_id,tracker_id)
			
api.add_resource(MultiChoiceLog,"/multiChoiceLogs/<int:id>")

api.add_resource(DeleteMultiChoice,"/multiChoiceLogs/<int:id>/<int:logID>")

api.add_resource(downloadMultiChoice,"/downloadMultiChoice/<int:tracker_id>")

#Defining auxilliary functions for the Dashboard API


#Defining a cache-friendly get function
@cache.memoize(60)
def get_helper_dashboard(user_id):
	user = User.query.filter_by(user_id = user_id).first()
	if user:
		trackers = Tracker.query.filter_by(user_id = user_id).all()
		if trackers:
			l= []
			for item in list(trackers):
				d={}
				d["tracker_id"] = item.tracker_id
				d["tracker_type"] = item.tracker_type
				d["tracker_name"] = item.tracker_name
				d["description"] = item.description
				d["tracker_last_logged"] = item.tracker_last_logged
				#print(type(item.tracker_last_logged))
				d["tracker_last_reviewed"] = item.tracker_last_reviewed
				l.append(d)
			return jsonify({"data":l,"status":"success"})
		else:
			return jsonify({"data":[],"status":"success"})
	else:
		abort(404,message = "The user specified doesn't have any trackers!")


#Defining Resoures for main dashboard

class Dashboard(Resource):
	ID=1

	@authtoken_required
	def get(self,user_id):
		#print("here")
		return get_helper_dashboard(user_id)
		
	@authtoken_required
	def post(self,user_id):
		#print("Here")
		user = User.query.filter_by(user_id = user_id).first()
		record = Tracker.query.filter_by(user_id = user_id, tracker_id = Dashboard.ID).first()
		flag = ""
		if record:
			flag = True
		else:
			flag = False
			
		while flag:
			record = Tracker.query.filter_by(user_id = user_id, tracker_id = Dashboard.ID).first()
			if record:
				flag = True
				Dashboard.ID+=1
			else:
				flag = False
		if user:
			args = request.get_json(force= True)
			try:
				if args["tracker_type"] in ["Numerical", "Multi Choice", "Time Duration", "Boolean"]:
						if (len(args["tracker_name"])>0 and len(args["description"])>0):
							newtracker = Tracker(tracker_id = Dashboard.ID, tracker_type = args["tracker_type"], tracker_name = args["tracker_name"], description = args["description"], user_id = user_id )
							Dashboard.ID+=1
							db.session.commit()
							db.session.add(newtracker)
							db.session.commit()
							cache.delete_memoized(get_helper_dashboard)
							return jsonify({"status":"success"})
						else:
							abc =  jsonify({"status":"failure","message":"Please enter all the fields!"})
							abc.status_code = 404
							return abc
				else:
						abort(404,message = "The Type of tracker needs to be among Numerical/Multi Choice/Boolean/Time Duration!")
				
			except:
				abc =  jsonify({"status":"failure","message":"Either some fields are missing or your tracker_type is not one among Numerical/Boolean/Time Duration/Boolean"})
				abc.status_code = 404
				return abc
			
		else:
			abort(404, message = "The user doesn't exist.")
	
	@authtoken_required
	def patch(self,user_id):
		user = User.query.filter_by(user_id = user_id).first()
		args = request.get_json(force= True)
		tracker_id = args["tracker_id"]
		tracker = Tracker.query.filter_by(user_id = user_id, tracker_id = tracker_id).first()
		if user and tracker:
			if args["name"]:
				tracker.tracker_name = args["name"]
			if args["description"]:
				tracker.description = args["description"]
			db.session.commit()
			cache.delete_memoized(get_helper_dashboard)
			return jsonify({"status":"success"})
		else:
			abort(404,message = "Either the tracker doesn't exist or the user doesn't exist.")

class DashboardDelete(Resource):

	@authtoken_required
	def delete(self,user_id,tracker_id):
		user = User.query.filter_by(user_id = user_id)
		tracker = Tracker.query.filter_by(user_id = user_id, tracker_id = tracker_id).first()
		if tracker and user:
			if tracker.tracker_type == "Multi Choice":
				trackers = Tracker_options_multi.query.filter_by(user_id = user_id, tracker_id = tracker_id).all()
				trackers = list(trackers)
				for item in trackers:
					db.session.delete(item)
				db.session.commit()
				logs = Tracker_multi_choice.query.filter_by(user_id = user_id,tracker_id = tracker_id).all()
				logs = list(logs)
				for item in logs:
					db.session.delete(item)
				db.session.commit()
				db.session.delete(tracker)
				db.session.commit()
				cache.delete_memoized(get_helper_dashboard)
				return jsonify({"status":"success"})
			elif tracker.tracker_type == "Numerical":
				logs = Tracker_Numerical.query.filter_by(user_id = user_id,tracker_id = tracker_id).all()
				logs = list(logs)
				for item in logs:
					db.session.delete(item)
				db.session.commit()
				db.session.delete(tracker)
				db.session.commit()
				cache.delete_memoized(get_helper_dashboard)
				return jsonify({"status":"success"})
			elif tracker.tracker_type == "Boolean":
				logs = Tracker_boolean.query.filter_by(user_id = user_id,tracker_id = tracker_id).all()
				logs = list(logs)
				for item in logs:
					db.session.delete(item)
				db.session.commit()
				db.session.delete(tracker)
				db.session.commit()
				cache.delete_memoized(get_helper_dashboard)
				return jsonify({"status":"success"})
			else:
				logs = Tracker_time_duration.query.filter_by(user_id = user_id,tracker_id = tracker_id).all()
				logs = list(logs)
				for item in logs:
					db.session.delete(item)
				db.session.commit()
				db.session.delete(tracker)
				db.session.commit()
				cache.delete_memoized(get_helper_dashboard)
				return jsonify({"status":"success"})
		else:
			abort(404,message = "Either the user doesn't exist or the tracker doesn't exist.")

class downloadDashboard(Resource):
	@authtoken_required
	def get(self,user_id):
		#print("Tracker ID")
		#print(tracker_id)
		user = User.query.filter_by(user_id = user_id).first()
		email_address = str(user.email)
		try:
			export_dashboard.delay(user_id)
			
		except:
			send_email(email_address,"Status of your Download","Your download could not be completed because the tracker details you gave may not exist.")	

#Adding the API endpoints

api.add_resource(Dashboard,"/dashboard")

api.add_resource(DashboardDelete,"/dashboard/<int:tracker_id>")

api.add_resource(downloadDashboard,"/downloadDashboard")


#Defining a resource for the User Model

class UserAPI(Resource):
	ID = 1
	def post(self):
		args = request.get_json(force= True)
		if (args["user_name"] and len(args["user_name"])>0 and args["password"] and len(args["password"])>0 and args["first_name"] and len(args["first_name"])>0 and args["last_name"] and len(args["last_name"])>0 and args["email"] and len(args["email"])>0):
			user = User.query.filter_by(user_name = args["user_name"]).first()
			if user:
				return jsonify({"status":"failed","message":"Please choose a different username"})
			else:
				record = User.query.filter_by(user_id = UserAPI.ID).first()
				flag = ""
			if record:
				flag = True
			else:
				flag = False
			
			while flag:
				record = User.query.filter_by(user_id = UserAPI.ID).first()
				if record:
					flag = True
					UserAPI.ID+=1
				else:
					flag = False
			url = None
			if len(args["url"])>0:
				url = args["url"]
			else:
				url = "https://chat.googleapis.com/v1/spaces/AAAAR4uXFxI/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=DJOWKezkjfOr6bKUQXVTI_DJtAUXBrgjlxkJ6bJUnVM%3D"
			newuser = User(user_id = UserAPI.ID,user_name = args["user_name"],first_name = args["first_name"],last_name = args["last_name"],password = args["password"], url = url, email = args["email"])
			UserAPI.ID+=1
			db.session.add(newuser)
			db.session.commit()
			return jsonify({"status":"success"})
		else:
			return jsonify({"status":"failed","message":"Please fill all the fields."})

api.add_resource(UserAPI,"/newUser")

@celery1.task()
def sendChat(user_id):
	date_today = str(date.today())
	user = User.query.filter_by(user_id = user_id).first()
    #print(date_today)
	url = str(user.url)
	name = (User.query.filter_by(user_id = user_id).first()).first_name
	message = {'text':f"Dear {name}, we see you haven't logged in records for some trackers today.Please log a value for them to stay on top of your wellbeing!"}
	headers = {'Content-Type':'appliction/json; charset = UTF-8'}
	http = httplib2.Http()
	trackers = Tracker.query.filter_by(user_id = user_id).all()
	trackers = list(trackers)
	flag = 0
	if len(trackers) ==0:
		return
	else:
		for item in trackers:
			#print(str(item.tracker_last_logged)[:10])
			if str(item.tracker_last_logged)[:10]<date_today:
				#print(str(item.tracker_last_logged)[:10])
				flag = 1
				
			if flag ==1:
				http.request(uri = url,method = "POST",headers = headers,body = json.dumps(message))
				break

@celery1.task()
def massChat():
	ids = list(User.query.filter_by().all())
	for item in ids:
		ID = item.user_id
		sendChat.delay(ID)

@celery1.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
		sender.add_periodic_task(crontab(hour = 18,minute = 0), massChat.s(), name='Daily Reminder')
		
@celery1.task()
def upload_dashboard(user_id,filename):
	user = User.query.filter_by(user_id = user_id).first()
	email_address = str(user.email)
	with open(filename, "r") as f:
		try:
			a = f.readline()
			a = f.readline()
		except:
			send_email(email_address,"Status of your Import","Your import could not be processed because you have not provided even one tracker to be imported.")
			return
		while (a):
			s = a.split(",")
			tracker_id = int(s[0])
			tracker = Tracker.query.filter_by(user_id = user_id, tracker_id = tracker_id).first()
			if tracker:
				a = f.readline()
				continue
			else:
				try:
					tracker_type = s[1]
					assert tracker_type in ["Multi Choice","Time Duration","Boolean","Numerical"]
					tracker_name = s[2]
					tracker_description = s[3]
					tracker_last_reviewed = datetime.datetime.strptime(s[4],'%Y-%m-%d %H:%M:%S.%f')
					tracker_last_logged = datetime.datetime.strptime(s[5][:-2],'%Y-%m-%d %H:%M:%S.%f')
					b = list(Tracker.query.filter_by(tracker_id=tracker_id,user_id = user_id, tracker_type = tracker_type, tracker_name = tracker_name, description = tracker_description, tracker_last_logged = tracker_last_logged, tracker_last_reviewed = tracker_last_reviewed).all())
					assert len(b) ==0
					tracker_new = Tracker(tracker_id=tracker_id,user_id = user_id, tracker_type = tracker_type, tracker_name = tracker_name, description = tracker_description, tracker_last_logged = tracker_last_logged, tracker_last_reviewed = tracker_last_reviewed)
					db.session.add(tracker_new)
					db.session.commit()
				except:
					a = f.readline()
					continue
		f.close()
	
	send_email(email_address,"Status of your Import","Your import has been successfully processed. Please review the dashboard to check the same. If some records don't show, it may be because the structure of the data in your file was not appropriate.")
	os.remove(filename)
	
	

class importJobTracker(Resource):
	@authtoken_required
	def post(self, user_id):
		user = User.query.filter_by(user_id = user_id).first()
		if user:
			file = request.files['UploadedFile']
			file.save(file.filename)
			upload_dashboard.delay(user_id,file.filename)
			cache.delete_memoized(get_helper_dashboard)			
		else:
			return jsonify({"status":"failure", "message":"You have not logged in"})


api.add_resource(importJobTracker,"/importJobTracker")

@celery1.task()
def upload_Boolean(user_id, filename, tracker_id):
	user = User.query.filter_by(user_id = user_id).first()
	email_address = str(user.email)
	with open(filename,"r") as f:
		try:
			a = f.readline()
			a = f.readline()
		except:
			send_email(email_address,"Status of your Import","Your import could not be processed because you have not provided even one log to be imported.")
			return
		logs = list(Tracker_boolean.query.filter_by(user_id = user_id, tracker_id = tracker_id).all())
		IDs = [item.tracker_log_id for item in logs]
		newID = max(IDs)
		while (a) : 
			try:
				s = a.split(",")
				tracker_value = str2bool(s[0])
				tracker_timestamp = datetime.datetime.strptime(s[1],'%Y-%m-%d %H:%M:%S.%f')
				tracker_notes = s[2][:-1]
				b = list(Tracker_boolean.query.filter_by(user_id = user_id, tracker_id = tracker_id, tracker_timestamp = tracker_timestamp, tracker_value = tracker_value).all())
				assert len(b) ==0
				log_new = Tracker_boolean(user_id = user_id, tracker_id = tracker_id, tracker_timestamp = tracker_timestamp, tracker_note = tracker_notes, tracker_value = tracker_value, tracker_log_id = newID+ 1)
				newID+=1
				db.session.add(log_new)
				db.session.commit()
				a = f.readline()
			except:
				a = f.readline()

		
		f.close()
	
	send_email(email_address,"Status of your Import","Your import has been successfully processed. Please review the boolean tracker log page to check the same. If some records don't show, it may be because the tracker doesn't exist or the structure of the data in your file was not appropriate.")
	os.remove(filename)
	


class importJobBoolean(Resource):
	@authtoken_required
	def post(self,user_id,tracker_id):
		tracker = Tracker.query.filter_by(user_id = user_id, tracker_id = tracker_id,tracker_type = "Boolean").first()
		user = User.query.filter_by(user_id = user_id).first()
		email_address = str(user.email)
		if tracker:
			file = request.files["UploadedFile"]
			file.save(file.filename)
			upload_Boolean.delay(user_id,file.filename,tracker_id)
			cache.delete_memoized(get_helper_boolean)
		else:
			send_email(email_address,"Status of your Import","Your import could not be completed because the tracker details you gave may not exist.")

api.add_resource(importJobBoolean,"/importJobBoolean/<int:tracker_id>")

@celery1.task()
def uploadNumerical(user_id,tracker_id,filename):
	user = User.query.filter_by(user_id = user_id).first()
	email_address = str(user.email)
	with open(filename,"r") as f:
		try:
			a = f.readline()
			a = f.readline()
		except:
			send_email(email_address,"Status of your Import","Your import could not be processed because you have not provided even one log to be imported.")
			return
		logs = list(Tracker_Numerical.query.filter_by(user_id = user_id, tracker_id = tracker_id).all())
		IDs = [item.tracker_log_id for item in logs]
		newID = max(IDs)
		while (a):
			try:
				s = a.split(",")
				tracker_value = float(s[0])
				tracker_timestamp = datetime.datetime.strptime(s[1],'%Y-%m-%d %H:%M:%S.%f')
				tracker_notes = s[2][:-1]
				b = list(Tracker_Numerical.query.filter_by(user_id = user_id, tracker_id = tracker_id, tracker_timestamp = tracker_timestamp,tracker_value = tracker_value).all())
				assert len(b) == 0
				log_new = Tracker_Numerical(user_id = user_id, tracker_id = tracker_id, tracker_timestamp = tracker_timestamp, tracker_note = tracker_notes, tracker_value = tracker_value, tracker_log_id = newID+ 1)
				newID+=1
				db.session.add(log_new)
				db.session.commit()
				a = f.readline()
			except:
				a = f.readline()
		f.close()
	send_email(email_address,"Status of your Import","Your import has been successfully processed. Please review the numerical tracker log page to check the same. If some records don't show, it may be because the tracker doesn't exist or the structure of the data in your file was not appropriate.")
	os.remove(filename)
	

class importJobNumerical(Resource):
	@authtoken_required
	def post(self,user_id, tracker_id):
		tracker = Tracker.query.filter_by(user_id = user_id, tracker_id = tracker_id, tracker_type = "Numerical").first()
		user = User.query.filter_by(user_id = user_id).first()
		email_address = str(user.email)
		if tracker:
			file = request.files["file"]
			file.save(file.filename)
			uploadNumerical.delay(user_id,tracker_id,file.filename)
			cache.delete_memoized(get_helper_numerical)	
			
		else:
			send_email(email_address,"Status of your Import","Your import could not be completed because the tracker details you gave may not exist.")

api.add_resource(importJobNumerical,"/importJobNumerical/<int:tracker_id>")

@celery1.task()
def uploadTimeDuration(user_id,tracker_id,filename):
	user = User.query.filter_by(user_id = user_id).first()
	email_address = str(user.email)
	with open(filename,"r") as f:
		try:
			a = f.readline()
			a = f.readline()
		except:
			send_email(email_address,"Status of your Import","Your import could not be processed because you have not provided even one log to be imported.")
			return
		logs = list(Tracker_time_duration.query.filter_by(user_id = user_id, tracker_id = tracker_id).all())
		IDs = [item.tracker_log_id for item in logs]
		newID = max(IDs)
		while (a):
			try:
				s = a.split(",")
				tracker_hours = int(s[0])
				tracker_minutes = int(s[1])
				tracker_timestamp = datetime.datetime.strptime(s[2],'%Y-%m-%d %H:%M:%S.%f')
				tracker_notes = s[3][:-1]
				b = list(Tracker_time_duration.query.filter_by(user_id = user_id, tracker_id = tracker_id, tracker_timestamp = tracker_timestamp, tracker_hours = tracker_hours, tracker_minutes = tracker_minutes).all())
				assert len(b) ==0
				log_new = Tracker_time_duration(user_id = user_id, tracker_id = tracker_id, tracker_timestamp = tracker_timestamp, tracker_note = tracker_notes, tracker_hours = tracker_hours, tracker_minutes = tracker_minutes,tracker_log_id = newID+ 1)
				newID+=1
				db.session.add(log_new)
				db.session.commit()
				a = f.readline()
			except:
				a = f.readline()
		f.close()
	
	send_email(email_address,"Status of your Import","Your import has been successfully processed. Please review the time duration log page to check the same. If some records don't show, it may be because the tracker doesn't exist or the structure of the data in your file was not appropriate.")
	os.remove(filename)
	
	

class importJobTimeDuration(Resource):
	@authtoken_required
	def post(self,user_id, tracker_id):
		tracker = Tracker.query.filter_by(user_id = user_id, tracker_id = tracker_id, tracker_type = "Time Duration").first()
		user = User.query.filter_by(user_id = user_id).first()
		email_address = str(user.email)
		if tracker:
			file = request.files["file"]
			file.save(file.filename)
			uploadTimeDuration.delay(user_id,tracker_id,file.filename)
			cache.delete_memoized(get_helper_time_duration)
		else:
			send_email(email_address,"Status of your Import","Your import could not be completed because the tracker details you gave may not exist.")

api.add_resource(importJobTimeDuration,"/importTimeDuration/<int:tracker_id>")

@celery1.task()
def upload_MultiChoice(user_id, filename, tracker_id):
	user = User.query.filter_by(user_id = user_id).first()
	email_address = str(user.email)
	
	with open(filename,"r") as f:
		try:
			a = f.readline()
			a = f.readline()
		except:
			send_email(email_address,"Status of your Import","Your import could not be processed because you have not provided even one log to be imported.")
			return
		logs = list(Tracker_multi_choice.query.filter_by(user_id = user_id, tracker_id = tracker_id).all())
		options = list(Tracker_options_multi.query.filter_by(user_id = user_id, tracker_id = tracker_id).all())
		option_values = [item.option for item in options]
		IDs = [item.tracker_log_id for item in logs]
		newID = max(IDs)
		while (a) : 
			s = a.split(",")
			tracker_value = s[0]
			try:
				assert s[0] in option_values
				tracker_timestamp = datetime.datetime.strptime(s[1],'%Y-%m-%d %H:%M:%S.%f')
				tracker_notes = s[2][:-1]
				b = list(Tracker_multi_choice.query.filter_by(user_id = user_id, tracker_id = tracker_id, tracker_timestamp = tracker_timestamp, tracker_value = tracker_value).all())
				assert len(b) ==0
				log_new = Tracker_multi_choice(user_id = user_id, tracker_id = tracker_id, tracker_timestamp = tracker_timestamp, tracker_note = tracker_notes, tracker_value = tracker_value, tracker_log_id = newID+ 1)
				newID+=1
				db.session.add(log_new)
				db.session.commit()
				a = f.readline()
			except:
				a = f.readline()
		
		f.close()
	
	send_email(email_address,"Status of your Import","Your import has been successfully processed. Please review the multi choice log page to check the same. If some records don't show, it may be because the tracker doesn't exist or the structure of the data in your file was not appropriate.")
	os.remove(filename)
	


class importMultiChoice(Resource):
	@authtoken_required
	def post(self,user_id,tracker_id):
		tracker = Tracker.query.filter_by(user_id = user_id, tracker_id = tracker_id,tracker_type = "Multi Choice").first()
		user = User.query.filter_by(user_id = user_id).first()
		email_address = str(user.email)
		if tracker:
			file = request.files["UploadedFile"]
			file.save(file.filename)
			upload_MultiChoice.delay(user_id,file.filename, tracker_id)
			cache.delete_memoized(get_multichoice_records_helper)		
		else:
			send_email(email_address,"Status of your Import","Your import could not be completed because the tracker details you gave may not exist.")

api.add_resource(importMultiChoice,"/importJobMultiChoice/<int:tracker_id>")

			
import weasyprint
import jinja2
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

@celery1.task()
def generate_dashboard_report_html(user_id):
	trackers = list(Tracker.query.filter_by(user_id = user_id).all())
	user = User.query.filter_by(user_id = user_id).first()
	records = []
	for tracker in trackers:
		d={}
		d["tracker_name"] = str(tracker.tracker_name)
		d["tracker_type"] = str(tracker.tracker_type)
		if d["tracker_type"] == "Numerical":
			items = []
			values = []
			times = []
			results = list(Tracker_Numerical.query.filter_by(user_id = user_id,tracker_id = tracker.tracker_id).all())
			for thing in results:
				e = {}
				e["logID"] = thing.tracker_log_id
				e["tracker_value"] = thing.tracker_value
				values.append(thing.tracker_value)
				e["tracker_note"] = thing.tracker_note
				e["tracker_timestamp"] = thing.tracker_timestamp
				times.append(thing.tracker_timestamp.strftime("%d %B %Y"))
				items.append(e)
			d["logs"] = items
			if(len(items)>0):
				data = pd.DataFrame.from_dict({"values":np.array(values), "times":np.array(times), "index":np.array([i+1 for i in range(len(values))])})
				fig = data.plot(kind = "line",x="times",y = "values",figsize=(10,10))
				fig.set_xlabel("Timestamps")
				fig.set_ylabel("Value of Tracker")
				plt.savefig(r"/home/arya/MAD2_Project_PWA/backend/static/"+ str(user_id)+ str(tracker.tracker_id)+ "plot.png")
				d["graph"] = "file:///home/arya/MAD2_Project_PWA/backend/static/"+ str(user_id)+ str(tracker.tracker_id)+ "plot.png"
			records.append(d)
		elif (d["tracker_type"] == "Boolean"):
			items = []
			values = []
			results = list(Tracker_boolean.query.filter_by(user_id = user_id, tracker_id = tracker.tracker_id).all())
			for thing in results:
				e = {}
				e["logID"] = thing.tracker_log_id
				e["tracker_value"] = thing.tracker_value
				values.append(thing.tracker_value)
				e["tracker_note"] = thing.tracker_note
				e["tracker_timestamp"] = thing.tracker_timestamp
				items.append(e)
			d["logs"] = items
			if len(items)>0:
				y_values = []
				y_values.append(values.count(True))
				y_values.append(values.count(False))
				#print(y_values)
				data = pd.DataFrame.from_dict({"values":np.array([True,False]),"counts": np.array(y_values), "index": np.array([i+1 for i in range(2)])})
				fig = data.plot(kind="bar",x = "values", y = "counts", figsize=(10,10))
				fig.set_xlabel("Values")
				fig.set_ylabel("Counts")
				plt.savefig(r"/home/arya/MAD2_Project_PWA/backend/static/"+ str(user_id)+ str(tracker.tracker_id)+ "plot.png")
				d["graph"] = "file:///home/arya/MAD2_Project_PWA/backend/static/"+ str(user_id)+ str(tracker.tracker_id)+ "plot.png"
			records.append(d)
		elif d["tracker_type"] == "Time Duration":
			items = []
			values = []
			times = []
			results = list(Tracker_time_duration.query.filter_by(user_id = user_id, tracker_id = tracker.tracker_id).all())
			for thing in results:
				e = {}
				e["logID"] = thing.tracker_log_id
				e["tracker_value"] = thing.tracker_hours*60 + thing.tracker_minutes
				values.append(e["tracker_value"])
				e["tracker_note"] = thing.tracker_note
				e["tracker_timestamp"] = thing.tracker_timestamp
				times.append(thing.tracker_timestamp.strftime("%d %B %Y"))
				items.append(e)
			d["logs"] = items
			if len(items)>0:
				data = pd.DataFrame.from_dict({"values":np.array(values), "times":np.array(times), "index":np.array([i+1 for i in range(len(values))])})
				fig = data.plot(kind = "line",x="times",y = "values", figsize=(10,10))
				fig.set_xlabel("Timestamps")
				fig.set_ylabel("Time Duration in Minutes")
				plt.savefig(r"/home/arya/MAD2_Project_PWA/backend/static/"+ str(user_id)+ str(tracker.tracker_id)+ "plot.png")
				d["graph"] = "file:///home/arya/MAD2_Project_PWA/backend/static/"+ str(user_id)+ str(tracker.tracker_id)+ "plot.png"
			records.append(d)
		else:
			items = []
			results = list(Tracker_multi_choice.query.filter_by(user_id = user_id, tracker_id = tracker.tracker_id).all())
			values = []
			uniques = list(Tracker_options_multi.query.filter_by(user_id = user_id, tracker_id = tracker.tracker_id).all())
			uniques = [str(item.option) for item in uniques]
			for thing in results:
				e = {}
				e["logID"] = thing.tracker_log_id
				e["tracker_value"] = thing.tracker_value
				values.append(thing.tracker_value)
				e["tracker_note"] = thing.tracker_note
				e["tracker_timestamp"] = thing.tracker_timestamp
				items.append(e)
			d["logs"] = items
			if len(items)>0:
				y_values = []
				for item in uniques:
					y_values.append(values.count(item))
				data = pd.DataFrame.from_dict({"values":np.array(uniques),"counts": np.array(y_values), "index": np.array([i+1 for i in range(len(uniques))])})
				fig = data.plot(kind = "bar",x = "values", y= "counts", figsize=(10,10))
				fig.set_xlabel("Options")
				fig.set_ylabel("Counts")
				plt.savefig(r"/home/arya/MAD2_Project_PWA/backend/static/"+ str(user_id)+ str(tracker.tracker_id)+ "plot.png")
				d["graph"] = "file:///home/arya/MAD2_Project_PWA/backend/static/"+ str(user_id)+ str(tracker.tracker_id)+ "plot.png"
			
			records.append(d)

	a = None
	with open("dashboard_report.html","r") as f:
		report_template = jinja2.Template(f.read())
		a = report_template.render(name = str(user.first_name),trackers = trackers, records = records)
		f.close()
	b = weasyprint.HTML(string = a)
	name = str(user_id)+"_dashboardreport.pdf"
	b.write_pdf(target = name)
	email = user.email
	name_user = str(user.first_name)
	send_email(email,"Monthly Progress Report",f"Dear {name_user}, please find attached your monthly progress and usage report. We hope to receive your continued support.",name)
	os.remove(name)
	for item in records:
		if "graph" in list(item.keys()):
			os.remove(item["graph"][7:])
	
	

@celery1.task()
def massreports():
	users = list(User.query.filter_by().all())
	for item in users:
		user_id = item.user_id
		generate_dashboard_report_html.delay(user_id)

@celery1.on_after_finalize.connect
def pdf_task(sender, **kwargs):
		sender.add_periodic_task(crontab(minute=0,hour = 5,day_of_month = 1), massreports.s(), name='Pdf Dashboard Report')
		
	
@celery1.task()
def password_revival(user_name,email):
	user = User.query.filter_by(user_name = user_name, email = email).first()
	if not user:
		send_email(email,"Status of your Password Revival","Sorry the details you have entered are not correct. Your password revival has failed.")
	else:
		password = str(user.password)
		send_email(email,"Status of your Password Revival",f"Your password revival has been successful and your password is {password}")
	return jsonify({"status":"success"})

class forgotPassword(Resource):
	def post(self):
		args = request.get_json(force=True)
		try:
			user_name = args["user_name"]
			email = args["email"]
		except:
			abort(404, message= "Please fill all the mandatory fields.")
		#print(email)
		return password_revival(user_name=user_name,email=email)

api.add_resource(forgotPassword,"/forgotPassword")




if __name__ =="__main__":
	app.debug=True
	app.run()


