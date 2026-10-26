"""
Demo Data Seeder for TaskFlow
Run this script to populate the database with sample data for testing
"""

from app import app
from models import db, User, Task
from datetime import datetime, timedelta
import random

def seed_demo_data():
    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        Task.query.delete()
        User.query.delete()
        db.session.commit()
        
        # Create demo users
        print("Creating demo users...")
        users = []
        
        # Main user
        user1 = User(username='john_doe', email='john@example.com')
        user1.set_password('password123')
        users.append(user1)
        
        # Team members
        user2 = User(username='sarah_smith', email='sarah@example.com')
        user2.set_password('password123')
        users.append(user2)
        
        user3 = User(username='mike_wilson', email='mike@example.com')
        user3.set_password('password123')
        users.append(user3)
        
        user4 = User(username='emily_brown', email='emily@example.com')
        user4.set_password('password123')
        users.append(user4)
        
        for user in users:
            db.session.add(user)
        
        db.session.commit()
        print(f"Created {len(users)} users")
        
        # Create demo tasks
        print("Creating demo tasks...")
        
        task_templates = [
            {
                'title': 'Complete Project Proposal',
                'description': 'Write and submit the Q4 project proposal including budget, timeline, and resource allocation.',
                'priority': 'high',
                'status': 'in_progress',
                'days_offset': 3
            },
            {
                'title': 'Review Code Documentation',
                'description': 'Go through the codebase and update all documentation to reflect recent changes.',
                'priority': 'medium',
                'status': 'todo',
                'days_offset': 7
            },
            {
                'title': 'Team Meeting Preparation',
                'description': 'Prepare slides and agenda for the weekly team sync meeting.',
                'priority': 'high',
                'status': 'todo',
                'days_offset': 1
            },
            {
                'title': 'Update User Interface',
                'description': 'Implement the new design mockups for the dashboard and user profile pages.',
                'priority': 'medium',
                'status': 'in_progress',
                'days_offset': 5
            },
            {
                'title': 'Database Optimization',
                'description': 'Analyze query performance and optimize slow database queries.',
                'priority': 'low',
                'status': 'todo',
                'days_offset': 10
            },
            {
                'title': 'Client Feedback Review',
                'description': 'Review and categorize all client feedback from the last sprint.',
                'priority': 'medium',
                'status': 'completed',
                'days_offset': -2
            },
            {
                'title': 'Security Audit',
                'description': 'Perform comprehensive security audit of the authentication system.',
                'priority': 'high',
                'status': 'todo',
                'days_offset': 2
            },
            {
                'title': 'Write Unit Tests',
                'description': 'Create unit tests for the new API endpoints to ensure 80% code coverage.',
                'priority': 'medium',
                'status': 'todo',
                'days_offset': 8
            },
            {
                'title': 'API Documentation',
                'description': 'Complete API documentation with examples and use cases.',
                'priority': 'low',
                'status': 'in_progress',
                'days_offset': 12
            },
            {
                'title': 'Bug Fix: Login Issues',
                'description': 'Investigate and fix the reported login timeout issues on mobile devices.',
                'priority': 'high',
                'status': 'completed',
                'days_offset': -5
            },
            {
                'title': 'Mobile App Testing',
                'description': 'Test the mobile application on various devices and screen sizes.',
                'priority': 'medium',
                'status': 'todo',
                'days_offset': 6
            },
            {
                'title': 'Backup Strategy Review',
                'description': 'Review current backup procedures and implement improvements.',
                'priority': 'high',
                'status': 'todo',
                'days_offset': -1
            },
            {
                'title': 'Performance Testing',
                'description': 'Run load tests and identify performance bottlenecks.',
                'priority': 'low',
                'status': 'todo',
                'days_offset': 15
            },
            {
                'title': 'Update Dependencies',
                'description': 'Update all project dependencies to latest stable versions.',
                'priority': 'low',
                'status': 'completed',
                'days_offset': -3
            },
            {
                'title': 'User Onboarding Flow',
                'description': 'Design and implement an improved user onboarding experience.',
                'priority': 'medium',
                'status': 'in_progress',
                'days_offset': 4
            }
        ]
        
        tasks = []
        for i, template in enumerate(task_templates):
            # Calculate deadline
            deadline = datetime.utcnow() + timedelta(days=template['days_offset'])
            
            # Randomly assign some tasks to other users
            owner = users[0]  # Most tasks owned by john_doe
            assigned_to = None
            
            if random.random() > 0.6:  # 40% chance of assignment
                assigned_to = random.choice(users[1:]).id
            
            task = Task(
                title=template['title'],
                description=template['description'],
                priority=template['priority'],
                status=template['status'],
                deadline=deadline,
                user_id=owner.id,
                assigned_to=assigned_to
            )
            
            # Set completed_at for completed tasks
            if template['status'] == 'completed':
                task.completed_at = deadline
            
            tasks.append(task)
            db.session.add(task)
        
        db.session.commit()
        print(f"Created {len(tasks)} tasks")
        
        print("\n" + "="*50)
        print("Demo data seeded successfully!")
        print("="*50)
        print("\nDemo User Credentials:")
        print("-" * 50)
        for user in users:
            print(f"Username: {user.username:20} Password: password123")
        print("-" * 50)
        print("\nLogin with any of these accounts to explore the application!")
        print("Recommended: Use 'john_doe' to see all the tasks")
        print("="*50)

if __name__ == '__main__':
    seed_demo_data()

