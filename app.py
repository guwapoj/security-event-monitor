from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Database Model
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(100), nullable=False)
    severity = db.Column(db.String(20), nullable=False)
    source_ip = db.Column(db.String(100))
    description = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "event_type": self.event_type,
            "severity": self.severity,
            "source_ip": self.source_ip,
            "description": self.description,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }

# Create database tables (Flask 3.x compatible)
with app.app_context():
    db.create_all()

# Routes

@app.route('/')
def home():
    return jsonify({"message": "✅ Security Event Monitoring API is running"}), 200


# Add a new security event
@app.route('/events', methods=['POST'])
def add_event():
    data = request.get_json()

    if not data or not data.get('event_type') or not data.get('severity'):
        return jsonify({"error": "Missing required fields: event_type and severity"}), 400

    new_event = Event(
        event_type=data['event_type'],
        severity=data['severity'],
        source_ip=data.get('source_ip'),
        description=data.get('description')
    )

    db.session.add(new_event)
    db.session.commit()

    return jsonify({"message": "Event added successfully", "event": new_event.to_dict()}), 201


# Get all events or filter by severity
@app.route('/events', methods=['GET'])
def get_events():
    severity = request.args.get('severity')

    if severity:
        events = Event.query.filter_by(severity=severity).all()
    else:
        events = Event.query.all()

    return jsonify([event.to_dict() for event in events]), 200


# Get a specific event by ID
@app.route('/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    event = Event.query.get(event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404

    return jsonify(event.to_dict()), 200


# Delete an event by ID
@app.route('/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    event = Event.query.get(event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404

    db.session.delete(event)
    db.session.commit()

    return jsonify({"message": "Event deleted successfully"}), 200



# Run the app
if __name__ == '__main__':
    app.run(debug=True)
