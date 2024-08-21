"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planets, Favorite, Person, Planet


app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# Rutas para los usuarios:

@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user.serialize()), 200

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Verifica si el usuario ya existe
    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({'error': 'User already exists'}), 400

    # Crea un nuevo usuario
    user = User(id=User.query.count() + 1, email=email, password=password, is_active=True)
    db.session.add(user)
    db.session.commit()
    return jsonify(user.serialize()), 201

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    data = request.get_json()
    for key, value in data.items():
        setattr(user, key, value)
    db.session.commit()
    return jsonify(user.serialize()), 200

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'}), 200

@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify([favorite.serialize() for favorite in user.favorites]), 200

# Rutas para People:

@app.route('/people', methods=['GET'])
def get_all_people():
    people = People.query.all()
    return jsonify([person.serialize() for person in people]), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    people = People.query.get(people_id)
    if not people:
        return jsonify({'error': 'Person not found'}), 404
    
    # Recuperar detalles completos desde Person
    person = Person.query.get(people.person_id)
    if not person:
        return jsonify({'error': 'Detailed Person not found'}), 404
    
    return jsonify(person.serialize()), 200

@app.route('/people', methods=['POST'])
def create_person():
    data = request.get_json()
    
    # Crear en Person (tabla detallada)
    person = Person(**data)
    db.session.add(person)
    db.session.commit()

    # Crear o actualizar en People (tabla resumida)
    people_data = {
        'name': person.name,
        'url': person.url,
        'person_id': person.id
    }
    people = People.query.filter_by(person_id=person.id).first()
    if not people:
        people = People(**people_data)
    else:
        for key, value in people_data.items():
            setattr(people, key, value)
    
    db.session.add(people)
    db.session.commit()
    
    return jsonify(person.serialize()), 201

@app.route('/people/<int:people_id>', methods=['PUT'])
def update_person(people_id):
    person = Person.query.get(people_id)
    if not person:
        return jsonify({'error': 'Person not found'}), 404
    
    data = request.get_json()
    for key, value in data.items():
        setattr(person, key, value)
    db.session.commit()

    # Actualizar People (tabla resumida)
    if person.people:
        person.people.name = person.name
        person.people.url = person.url
        db.session.commit()
    
    return jsonify(person.serialize()), 200

@app.route('/people/<int:people_id>', methods=['DELETE'])
def delete_person(people_id):
    person = Person.query.get(people_id)
    if not person:
        return jsonify({'error': 'Person not found'}), 404
    
    # Eliminar People asociado
    if person.people:
        db.session.delete(person.people)
    
    db.session.delete(person)
    db.session.commit()
    return jsonify({'message': 'Person deleted'}), 200

# Rutas para planetas:

@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planets.query.all()
    return jsonify([planet.serialize() for planet in planets]), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planets = Planets.query.get(planet_id)
    if not planets:
        return jsonify({'error': 'Planet not found'}), 404
    
    # Recuperar detalles completos desde Planet
    planet = Planet.query.get(planets.planet_id)
    if not planet:
        return jsonify({'error': 'Detailed Planet not found'}), 404
    
    return jsonify(planet.serialize()), 200

@app.route('/planets', methods=['POST'])
def create_planet():
    data = request.get_json()
    
    # Crear en Planet (tabla detallada)
    planet = Planet(**data)
    db.session.add(planet)
    db.session.commit()

    # Crear o actualizar en Planets (tabla resumida)
    planets_data = {
        'name': planet.name,
        'url': planet.url,
        'planet_id': planet.id
    }
    planets = Planets.query.filter_by(planet_id=planet.id).first()
    if not planets:
        planets = Planets(**planets_data)
    else:
        for key, value in planets_data.items():
            setattr(planets, key, value)
    
    db.session.add(planets)
    db.session.commit()
    
    return jsonify(planet.serialize()), 201

@app.route('/planets/<int:planet_id>', methods=['PUT'])
def update_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({'error': 'Planet not found'}), 404
    
    data = request.get_json()
    for key, value in data.items():
        setattr(planet, key, value)
    db.session.commit()

    # Actualizar Planets (tabla resumida)
    if planet.planets:
        planet.planets.name = planet.name
        planet.planets.url = planet.url
        db.session.commit()
    
    return jsonify(planet.serialize()), 200

@app.route('/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({'error': 'Planet not found'}), 404
    
    # Eliminar Planets asociado
    if planet.planets:
        db.session.delete(planet.planets)
    
    db.session.delete(planet)
    db.session.commit()
    return jsonify({'message': 'Planet deleted'}), 200

# Rutas para favoritos:

@app.route('/favorites', methods=['GET'])
def get_all_favorites():
    favorites = Favorite.query.all()
    return jsonify([favorite.serialize() for favorite in favorites]), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def create_planet_favorite(planet_id):
    data = request.get_json()
    user_id = data.get('user_id')

    # Verifica si el usuario y el planeta existen
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    planet = Planets.query.get(planet_id)
    if not planet:
        return jsonify({'error': 'Planet not found'}), 404

    # Crea un nuevo favorito
    favorite = Favorite(user_id=user.id, planet_id=planet.id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify(favorite.serialize()), 201

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def create_people_favorite(people_id):
    data = request.get_json()
    user_id = data.get('user_id')

    # Verifica si el usuario y la persona existen
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    person = People.query.get(people_id)
    if not person:
        return jsonify({'error': 'Person not found'}), 404

    # Crea un nuevo favorito
    favorite = Favorite(user_id=user.id, people_id=person.id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify(favorite.serialize()), 201

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_planet_favorite(planet_id):
    data = request.get_json()
    user_id = data.get('user_id')

    # Busca el favorito y elimínalo
    favorite = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if not favorite:
        return jsonify({'error': 'Favorite not found'}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({'message': 'Favorite deleted'}), 200

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_people_favorite(people_id):
    data = request.get_json()
    user_id = data.get('user_id')

    # Busca el favorito y elimínalo
    favorite = Favorite.query.filter_by(user_id=user_id, people_id=people_id).first()
    if not favorite:
        return jsonify({'error': 'Favorite not found'}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({'message': 'Favorite deleted'}), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)