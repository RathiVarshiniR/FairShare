"""
User model for authentication and user data
"""

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

# Import db from extensions, not from app
from extensions import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    owned_projects = db.relationship('Project', backref='owner', lazy=True)
    tasks_assigned = db.relationship('Task', foreign_keys='Task.assigned_to', backref='assignee', lazy=True)
    activities = db.relationship('ActivityLog', backref='user', lazy=True)
    ratings_given = db.relationship('PeerRating', foreign_keys='PeerRating.rater_id', backref='rater', lazy=True)
    ratings_received = db.relationship('PeerRating', foreign_keys='PeerRating.rated_user_id', backref='rated_user', lazy=True)
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_fairness_score(self, project_id):
        """Calculate fairness score for a user in a specific project"""
        # Import other models here to avoid circular imports
        from models.task import Task
        from models.activity import ActivityLog
        from models.peer_rating import PeerRating
        
        # Get all tasks assigned to user in this project
        tasks = Task.query.filter_by(
            project_id=project_id,
            assigned_to=self.id
        ).all()
        
        if not tasks:
            return {
                'score': 0,
                'tag': 'No Tasks',
                'metrics': {
                    'tasks_completed': '0/0',
                    'on_time_rate': '0/0',
                    'activity_count': 0,
                    'peer_rating': 'No ratings'
                }
            }
        
        # Calculate metrics
        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.status == 'completed')
        
        # 40% - Tasks completed
        task_score = (completed_tasks / total_tasks) * 40 if total_tasks > 0 else 0
        
        # 30% - On-time submissions
        on_time_tasks = sum(1 for t in tasks if t.status == 'completed' and 
                           t.completed_at and t.deadline and t.completed_at <= t.deadline)
        on_time_score = (on_time_tasks / total_tasks) * 30 if total_tasks > 0 else 0
        
        # 20% - Activity level (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_activities = ActivityLog.query.filter(
            ActivityLog.user_id == self.id,
            ActivityLog.project_id == project_id,
            ActivityLog.timestamp >= thirty_days_ago
        ).count()
        activity_score = min(20, (recent_activities / 10) * 20)
        
        # 10% - Peer ratings
        ratings = PeerRating.query.filter_by(
            project_id=project_id,
            rated_user_id=self.id
        ).all()
        avg_rating = sum(r.rating for r in ratings) / len(ratings) if ratings else 3
        peer_score = (avg_rating / 5) * 10
        
        # Calculate total score
        total_score = task_score + on_time_score + activity_score + peer_score
        
        # Determine tag
        if total_score >= 80:
            tag = "Top Contributor"
        elif total_score >= 50:
            tag = "Average"
        else:
            tag = "Needs Improvement"
        
        return {
            'score': round(total_score, 1),
            'tag': tag,
            'metrics': {
                'tasks_completed': f"{completed_tasks}/{total_tasks}",
                'on_time_rate': f"{on_time_tasks}/{total_tasks}",
                'activity_count': recent_activities,
                'peer_rating': round(avg_rating, 1) if ratings else 'No ratings'
            }
        }
    
    def __repr__(self):
        return f'<User {self.email}>'