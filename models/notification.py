"""
Notification model for task completions and updates
"""

from extensions import db
from datetime import datetime

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    message = db.Column(db.String(200), nullable=False)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='notifications', lazy=True)
    project = db.relationship('Project', backref='notifications', lazy=True)
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.read = True
        db.session.commit()
    
    def __repr__(self):
        return f'<Notification {self.message[:30]}>'