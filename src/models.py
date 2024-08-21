from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class BaseModel(db.Model):
    __abstract__ = True

    def __init__(self, **kwargs):
        columnas_filtradas = {key: kwargs[key] for key in kwargs if key in self.__table__.columns.keys()}
        for key, value in columnas_filtradas.items():
            setattr(self, key, value)

    def to_json(self):
        return json.dumps({column.name: getattr(self, column.name) for column in self.__table__.columns})

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.to_json()}>"
    
class Favorite(BaseModel):
    __tablename__ = 'favorites'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'))
    people_id = db.Column(db.Integer, db.ForeignKey('people.id'))

    user = db.relationship('User', back_populates='favorites')
    planet = db.relationship('Planets', back_populates='favorites')
    people = db.relationship('People', back_populates='favorites')

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "planet_id": self.planet_id,
            "people_id": self.people_id
        }

class User(BaseModel):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    is_active = db.Column(db.Boolean(), nullable=False)
    favorites = db.relationship('Favorite', back_populates='user', lazy=True)

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active
        }

class People(BaseModel):
    __tablename__ = 'people'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    url = db.Column(db.String(450), unique=True, nullable=False)
    
    # Relación uno a uno con Person
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    person = db.relationship('Person', back_populates='people', uselist=False)

    favorites = db.relationship('Favorite', back_populates='people')

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "person_id": self.person_id
        }

class Planets(BaseModel):
    __tablename__ = 'planets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    url = db.Column(db.String(450), unique=True, nullable=False)
    
    # Relación uno a uno con Planet
    planet_id = db.Column(db.Integer, db.ForeignKey('planet.id'))
    planet = db.relationship('Planet', back_populates='planets', uselist=False)

    favorites = db.relationship('Favorite', back_populates='planet')

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "planet_id": self.planet_id
        }

class Person(BaseModel):
    __tablename__ = 'person'
    id = db.Column(db.Integer, primary_key=True)
    birth_year = db.Column(db.String(150), nullable=False)
    eye_color = db.Column(db.String(150), nullable=False)
    films = db.Column(db.ARRAY(db.String), nullable=False)
    gender = db.Column(db.String(150), nullable=False)
    hair_color = db.Column(db.String(150), nullable=False)
    height = db.Column(db.String(150), nullable=False)
    homeworld = db.Column(db.String(150), nullable=False)
    mass = db.Column(db.String(150), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    skin_color = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    edited_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    species = db.Column(db.ARRAY(db.String), nullable=False)
    starships = db.Column(db.ARRAY(db.String), nullable=False)
    url = db.Column(db.String(150), nullable=False)
    vehicles = db.Column(db.ARRAY(db.String), nullable=False)
    
    # Relación uno a uno con People
    people = db.relationship('People', back_populates='person', uselist=False)

    def serialize(self):
        return {
            "id": self.id,
            "birth_year": self.birth_year,
            "eye_color": self.eye_color,
            "films": self.films,
            "gender": self.gender,
            "hair_color": self.hair_color,
            "height": self.height,
            "homeworld": self.homeworld,
            "mass": self.mass,
            "name": self.name,
            "skin_color": self.skin_color,
            "created_at": self.created_at.isoformat(),
            "edited_at": self.edited_at.isoformat(),
            "species": self.species,
            "starships": self.starships,
            "url": self.url,
            "vehicles": self.vehicles
        }

class Planet(BaseModel):
    __tablename__= 'planet'
    id = db.Column(db.Integer, primary_key=True)
    climate = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    edited_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    diameter = db.Column(db.String(150), nullable=False)
    films = db.Column(db.ARRAY(db.String), nullable=False)
    gravity = db.Column(db.String(150), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    orbital_period = db.Column(db.String(150), nullable=False)
    population = db.Column(db.String(150), nullable=False)
    residents = db.Column(db.ARRAY(db.String), nullable=False)
    rotation_period = db.Column(db.String(150), nullable=False)
    surface_water = db.Column(db.String(150), nullable=False)
    terrain = db.Column(db.String(150), nullable=False)
    url = db.Column(db.String(150), nullable=False)
    
    # Relación uno a uno con Planets
    planets = db.relationship('Planets', back_populates='planet', uselist=False)

    def serialize(self):
        return {
            "id": self.id,
            "climate": self.climate,
            "created_at": self.created_at.isoformat(),
            "edited_at": self.edited_at.isoformat(),
            "diameter": self.diameter,
            "films": self.films,
            "gravity": self.gravity,
            "name": self.name,
            "orbital_period": self.orbital_period,
            "population": self.population,
            "residents": self.residents,
            "rotation_period": self.rotation_period,
            "surface_water": self.surface_water,
            "terrain": self.terrain,
            "url": self.url
        }