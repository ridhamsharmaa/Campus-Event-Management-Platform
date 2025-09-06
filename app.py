from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ---------------------- MODELS ----------------------

class College(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    college_id = db.Column(db.Integer, db.ForeignKey('college.id'), nullable=False)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # Workshop, Fest, Seminar
    date = db.Column(db.String(50), nullable=False)
    college_id = db.Column(db.Integer, db.ForeignKey('college.id'), nullable=False)


class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('student_id', 'event_id', name='unique_registration'),)


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    present = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(20), nullable=False)  # Present, Absent, Excused


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1–5


# ---------------------- ROUTES ----------------------

@app.route("/")
def home():
    return {"message": "Campus Event Reporting System API is running"}

@app.route("/students", methods=["POST"])
def create_student():
    data = request.json
    student = Student(name=data["name"], email=data["email"], college_id=data["college_id"])
    db.session.add(student)
    db.session.commit()
    return jsonify({"id": student.id, "name": student.name})


# ---- Create Event ----
@app.route("/events", methods=["POST"])
def create_event():
    data = request.json
    event = Event(
        title=data['title'],
        type=data['type'],   # 👈 here
        date=data['date'],
        college_id=data['college_id']
    )
    db.session.add(event)
    db.session.commit()
    return jsonify({"message": "Event created", "event_id": event.id})


# ---- Register Student ----
@app.route("/register", methods=["POST"])
def register_student():
    data = request.json
    try:
        registration = Registration(student_id=data['student_id'], event_id=data['event_id'])
        db.session.add(registration)
        db.session.commit()
        return jsonify({"message": "Student registered"})
    except:
        return jsonify({"error": "Duplicate registration"}), 400


# ---- Mark Attendance ----
@app.route("/attendance", methods=["POST"])
def mark_attendance():
    data = request.json
    attendance = Attendance(student_id=data['student_id'], event_id=data['event_id'], status=data['status'])
    db.session.add(attendance)
    db.session.commit()
    return jsonify({"message": "Attendance marked"})


# ---- Submit Feedback ----
@app.route("/feedback", methods=["POST"])
def submit_feedback():
    data = request.json
    feedback = Feedback(student_id=data['student_id'], event_id=data['event_id'], rating=data['rating'])
    db.session.add(feedback)
    db.session.commit()
    return jsonify({"message": "Feedback submitted"})

@app.route("/colleges", methods=["POST"])
def create_college():
    data = request.json
    college = College(name=data["name"])
    db.session.add(college)
    db.session.commit()
    return jsonify({"id": college.id, "name": college.name})
# ---------------------- REPORTS ----------------------

# Event Popularity Report
@app.route("/reports/event-popularity", methods=["GET"])
def event_popularity():
    results = db.session.query(Event.title, func.count(Registration.id).label("registrations")) \
        .join(Registration, Registration.event_id == Event.id, isouter=True) \
        .group_by(Event.id) \
        .order_by(func.count(Registration.id).desc()).all()
    return jsonify([{"event": r[0], "registrations": r[1]} for r in results])


@app.route("/reports/student/<int:student_id>", methods=["GET"])
def student_participation(student_id):
    results = (
        db.session.query(Event.title)
        .join(Attendance, Event.id == Attendance.event_id)
        .filter(Attendance.student_id == student_id, Attendance.present == True)
        .all()
    )

    events = [r[0] for r in results]

    return jsonify({
        "student_id": student_id,
        "events_attended": events
    })



# Top 3 Most Active Students
@app.route("/reports/top-students", methods=["GET"])
def top_students():
    results = db.session.query(Student.name, func.count(Attendance.id).label("events")) \
        .join(Attendance, Attendance.student_id == Student.id) \
        .filter(Attendance.status == "Present") \
        .group_by(Student.id) \
        .order_by(func.count(Attendance.id).desc()).limit(3).all()
    return jsonify([{"student": r[0], "events_attended": r[1]} for r in results])


# Filter Events by Type
@app.route("/reports/filter", methods=["GET"])
def filter_events():
    event_type = request.args.get("type")
    results = Event.query.filter(func.lower(Event.type) == func.lower(event_type)).all()
    return jsonify([{"id": e.id, "title": e.title, "date": e.date, "type": e.type} for e in results])


# ---------------------- MAIN ----------------------

if __name__ == "__main__":
    print(app.url_map)

    with app.app_context():
        db.create_all()  # This creates all tables (Event, Student, etc.)
    app.run(debug=True)

