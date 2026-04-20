"""
Task model for project tasks
"""

from extensions import db
from datetime import datetime

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='not_started')  # not_started, in_progress, completed
    deadline = db.Column(db.DateTime, nullable=False)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    progress = db.Column(db.Integer, default=0)  # 0-100
    
    # Relationships
    activity_logs = db.relationship('ActivityLog', backref='task', lazy=True, cascade='all, delete-orphan')
    
    def update_status(self, new_status):
        """Update task status and log activity"""
        from models.activity import ActivityLog
        from models.notification import Notification
        from models.project import ProjectMember
        from models.user import User
        
        old_status = self.status
        self.status = new_status
        
        # If task is being marked as completed
        if new_status == 'completed' and not self.completed_at:
            self.completed_at = datetime.utcnow()
            self.progress = 100
            
            # Log the completion activity
            activity = ActivityLog(
                user_id=self.assigned_to,
                task_id=self.id,
                project_id=self.project_id,
                action=f"completed task: {self.title}"
            )
            db.session.add(activity)
            
            # Get the user who completed the task
            user = User.query.get(self.assigned_to)
            
            # Get all project members to notify
            members = ProjectMember.query.filter_by(project_id=self.project_id).all()
            
            # Create notification for each team member (except the one who completed it)
            for member in members:
                if member.user_id != self.assigned_to:
                    notification = Notification(
                        user_id=member.user_id,
                        project_id=self.project_id,
                        message=f"✅ Task '{self.title}' was completed by {user.name}"
                    )
                    db.session.add(notification)
        
        # If task is being marked as in progress
        elif new_status == 'in_progress' and old_status == 'not_started':
            activity = ActivityLog(
                user_id=self.assigned_to,
                task_id=self.id,
                project_id=self.project_id,
                action=f"started working on task: {self.title}"
            )
            db.session.add(activity)
        
        # Log status change
        activity = ActivityLog(
            user_id=self.assigned_to,
            task_id=self.id,
            project_id=self.project_id,
            action=f"changed task status from {old_status.replace('_', ' ')} to {new_status.replace('_', ' ')}"
        )
        db.session.add(activity)
        
        db.session.commit()
    
    def update_progress(self, progress_value):
        """Update task progress and log activity"""
        from models.activity import ActivityLog
        from models.notification import Notification
        from models.project import ProjectMember
        from models.user import User
        
        old_progress = self.progress
        self.progress = min(100, max(0, progress_value))
        
        # If progress reaches 100%, auto-complete the task
        if self.progress == 100 and self.status != 'completed':
            self.status = 'completed'
            self.completed_at = datetime.utcnow()
            
            # Log completion activity
            activity = ActivityLog(
                user_id=self.assigned_to,
                task_id=self.id,
                project_id=self.project_id,
                action=f"completed task: {self.title}"
            )
            db.session.add(activity)
            
            # Get the user who completed the task
            user = User.query.get(self.assigned_to)
            
            # Get all project members to notify
            members = ProjectMember.query.filter_by(project_id=self.project_id).all()
            
            # Create notification for each team member (except the one who completed it)
            for member in members:
                if member.user_id != self.assigned_to:
                    notification = Notification(
                        user_id=member.user_id,
                        project_id=self.project_id,
                        message=f"✅ Task '{self.title}' was completed by {user.name}"
                    )
                    db.session.add(notification)
        
        # If progress > 0 and task was not started, mark as in progress
        elif self.progress > 0 and self.status == 'not_started':
            self.status = 'in_progress'
            activity = ActivityLog(
                user_id=self.assigned_to,
                task_id=self.id,
                project_id=self.project_id,
                action=f"started working on task: {self.title}"
            )
            db.session.add(activity)
        
        # Log progress update
        activity = ActivityLog(
            user_id=self.assigned_to,
            task_id=self.id,
            project_id=self.project_id,
            action=f"updated progress from {old_progress}% to {self.progress}%"
        )
        db.session.add(activity)
        
        db.session.commit()
    
    @property
    def priority_color(self):
        """Get color for priority display"""
        colors = {
            'low': '#10b981',   # green
            'medium': '#f59e0b', # orange
            'high': '#ef4444'    # red
        }
        return colors.get(self.priority, '#6b7280')
    
    @property
    def status_color(self):
        """Get color for status display"""
        colors = {
            'not_started': '#6b7280',  # gray
            'in_progress': '#3b82f6',  # blue
            'completed': '#10b981'     # green
        }
        return colors.get(self.status, '#6b7280')
    
    @property
    def status_display(self):
        """Get human-readable status"""
        displays = {
            'not_started': 'Not Started',
            'in_progress': 'In Progress',
            'completed': 'Completed'
        }
        return displays.get(self.status, self.status)
    
    @property
    def priority_display(self):
        """Get human-readable priority"""
        displays = {
            'low': 'Low',
            'medium': 'Medium',
            'high': 'High'
        }
        return displays.get(self.priority, self.priority)
    
    def is_overdue(self):
        """Check if task is overdue"""
        if self.status == 'completed':
            return False
        return datetime.utcnow() > self.deadline
    
    def days_remaining(self):
        """Get days remaining until deadline"""
        if self.status == 'completed':
            return 0
        delta = self.deadline - datetime.utcnow()
        return max(0, delta.days)
    
    def __repr__(self):
        return f'<Task {self.title}>'