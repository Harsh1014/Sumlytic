from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    image_url = db.Column(db.String(500))
    price = db.Column(db.String(50))
    rating = db.Column(db.Float)
    platform = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_analyzed = db.Column(db.DateTime)
    
    # Relationships
    reviews = db.relationship('Review', backref='product', lazy=True, cascade='all, delete-orphan')
    analyses = db.relationship('Analysis', backref='product', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'name': self.name,
            'image_url': self.image_url,
            'price': self.price,
            'rating': self.rating,
            'platform': self.platform,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_analyzed': self.last_analyzed.isoformat() if self.last_analyzed else None
        }

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer)
    author = db.Column(db.String(100))
    date = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'text': self.text,
            'rating': self.rating,
            'author': self.author,
            'date': self.date,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Analysis(db.Model):
    __tablename__ = 'analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    total_reviews = db.Column(db.Integer, nullable=False)
    summary_pros = db.Column(db.JSON)
    summary_cons = db.Column(db.JSON)
    sentiment_positive = db.Column(db.Float)
    sentiment_neutral = db.Column(db.Float)
    sentiment_negative = db.Column(db.Float)
    key_features = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'total_reviews': self.total_reviews,
            'summary_pros': self.summary_pros,
            'summary_cons': self.summary_cons,
            'sentiment': {
                'positive': self.sentiment_positive,
                'neutral': self.sentiment_neutral,
                'negative': self.sentiment_negative
            },
            'key_features': self.key_features,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
