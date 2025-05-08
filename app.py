from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from textblob import TextBlob
from models import db, User, Comment

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'message': 'Usuario ya existe'}), 400

    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Usuario registrado con éxito'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username, password=password).first()
    if user:
        return jsonify({'success': True, 'user_id': user.id})
    else:
        return jsonify({'success': False, 'message': 'Credenciales inválidas'}), 401

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    comment_text = data.get('comment')
    user_id = data.get('user_id')

    analysis = TextBlob(comment_text)
    polarity = analysis.sentiment.polarity

    if polarity > 0:
        sentiment = 'Positivo'
    elif polarity < 0:
        sentiment = 'Negativo'
    else:
        sentiment = 'Neutro'

    comment = Comment(text=comment_text, sentiment=sentiment, user_id=user_id)
    db.session.add(comment)
    db.session.commit()

    return jsonify({'sentiment': sentiment})

@app.route('/history/<int:user_id>', methods=['GET'])
def history(user_id):
    comments = Comment.query.filter_by(user_id=user_id).all()
    result = [{'text': c.text, 'sentiment': c.sentiment} for c in comments]
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=8000)