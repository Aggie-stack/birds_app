import os
from flask import Flask, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api, Resource

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URI',
    'sqlite:///birds.db'  # fallback for local dev
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Initialize DB
db = SQLAlchemy(app)
migrate = Migrate(app, db)
api = Api(app)

# --- Models ---
class Bird(db.Model):
    __tablename__ = 'birds'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(50), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color
        }

# --- Seed function (run only if DB empty) ---
def seed_data():
    if Bird.query.count() == 0:
        bird1 = Bird(name="Parrot", color="Green")
        bird2 = Bird(name="Sparrow", color="Brown")
        db.session.add_all([bird1, bird2])
        db.session.commit()

# --- Routes ---
@app.route("/")
def home():
    return "Birds API is running! Visit /birds for data."

class Birds(Resource):
    def get(self):
        try:
            birds = [bird.to_dict() for bird in Bird.query.all()]
            return make_response(jsonify(birds), 200)
        except Exception as e:
            return make_response(jsonify({"message": str(e)}), 500)

api.add_resource(Birds, '/birds')

# --- Run App ---
if __name__ == "__main__":
    with app.app_context():
        db.create_all()   # Ensure tables exist
        seed_data()       # Seed sample birds
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
