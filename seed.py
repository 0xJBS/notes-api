"""
Database seed script - Populate the database with sample data for testing.

Run with: python seed.py
"""

from app import app, db
from models import User, Note
from faker import Faker

fake = Faker()


def seed_database():
    """Clear and repopulate the database with sample data"""
    
    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        db.drop_all()
        
        # Create tables
        print("Creating tables...")
        db.create_all()
        
        # Create sample users
        print("Creating sample users...")
        users = []
        
        user1 = User(username='alice', email='alice@example.com')
        user1.set_password('password123')
        users.append(user1)
        
        user2 = User(username='bob', email='bob@example.com')
        user2.set_password('password456')
        users.append(user2)
        
        user3 = User(username='charlie', email='charlie@example.com')
        user3.set_password('password789')
        users.append(user3)
        
        # Add users to session
        for user in users:
            db.session.add(user)
        
        db.session.commit()
        
        # Create sample notes for each user
        print("Creating sample notes...")
        
        note_titles = [
            'Daily standup notes',
            'Project ideas',
            'Personal goals',
            'Meeting notes',
            'Learning resources',
            'Bug fixes needed',
            'Travel plans',
            'Recipe ideas',
        ]
        
        for user in users:
            # Create 5-8 notes per user
            num_notes = fake.random_int(min=5, max=8)
            for i in range(num_notes):
                note = Note(
                    title=f"{note_titles[i % len(note_titles)]} - {user.username}",
                    content=fake.paragraph(nb_sentences=5),
                    user_id=user.id
                )
                db.session.add(note)
        
        db.session.commit()
        
        # Print summary
        print("\n✓ Database seeded successfully!")
        print(f"  - Users created: {User.query.count()}")
        print(f"  - Notes created: {Note.query.count()}")
        print("\nTest credentials:")
        for user in users:
            print(f"  - Username: {user.username}, Password: 'password{123+users.index(user)*111}'")


if __name__ == '__main__':
    seed_database()
