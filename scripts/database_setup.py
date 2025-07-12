import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app import app
from backend.database.db import db
from sqlalchemy import inspect
from backend.database.models import Product, Review, Analysis  # Moved above app context

def create_database():
    """Create all database tables"""
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created successfully!")
            
            from sqlalchemy import inspect
            tables = inspect(db.engine).get_table_names()
            print(f"📋 Created tables: {', '.join(tables)}")
            
        except Exception as e:
            print(f"❌ Error creating database: {str(e)}")

def seed_sample_data():
    """Add some sample data for testing"""
    with app.app_context():
        try:
            if Product.query.first():
                print("📊 Sample data already exists")
                return
            
            sample_product = Product(
                url="https://www.flipkart.com/sample-product",
                name="Sample Wireless Headphones",
                image_url="/placeholder.svg?height=200&width=200",
                price="2999",
                rating=4.2,
                platform="flipkart"
            )
            db.session.add(sample_product)
            db.session.flush()  # safer than commit when adding reviews right after

            sample_reviews = [
                Review(
                    product_id=sample_product.id,
                    text="Great sound quality and comfortable to wear for long hours. Battery life is excellent.",
                    rating=5,
                    author="John D."
                ),
                Review(
                    product_id=sample_product.id,
                    text="Good product but a bit expensive. Sound quality is decent.",
                    rating=3,
                    author="Sarah M."
                ),
                Review(
                    product_id=sample_product.id,
                    text="Amazing noise cancellation feature. Worth every penny!",
                    rating=5,
                    author="Mike R."
                )
            ]
            db.session.add_all(sample_reviews)
            db.session.commit()
            print("✅ Sample data added successfully!")
        except Exception as e:
            print(f"❌ Error adding sample data: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    print("🚀 Setting up Review Summarizer Database...")
    create_database()
    seed_sample_data()
    print("🎉 Database setup complete!")
