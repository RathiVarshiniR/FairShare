"""
Project and ProjectMember models
"""
from extensions import db
from datetime import datetime, timedelta

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    deadline = db.Column(db.DateTime, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    members = db.relationship('ProjectMember', backref='project', lazy=True, cascade='all, delete-orphan')
    tasks = db.relationship('Task', backref='project', lazy=True, cascade='all, delete-orphan')
    activity_logs = db.relationship('ActivityLog', backref='project', lazy=True)
    peer_ratings = db.relationship('PeerRating', backref='project', lazy=True, cascade='all, delete-orphan')
    
    def get_members_with_scores(self):
        """Get all members with their fairness scores"""
        from models.user import User
        
        members_with_scores = []
        for member in self.members:
            user = User.query.get(member.user_id)
            if user:
                score_data = user.get_fairness_score(self.id)
                members_with_scores.append({
                    'user': user,
                    'score': score_data['score'],
                    'tag': score_data['tag'],
                    'metrics': score_data['metrics']
                })
        
        return sorted(members_with_scores, key=lambda x: x['score'], reverse=True)
    
    def check_lazy_members(self, days_inactive=7):
        """Check for members with no activity for X days"""
        from models.activity import ActivityLog
        from models.user import User
        
        threshold = datetime.utcnow() - timedelta(days=days_inactive)
        lazy_members = []
        
        for member in self.members:
            last_activity = ActivityLog.query.filter_by(
                user_id=member.user_id,
                project_id=self.id
            ).order_by(ActivityLog.timestamp.desc()).first()
            
            if not last_activity or last_activity.timestamp < threshold:
                user = User.query.get(member.user_id)
                lazy_members.append({
                    'user': user,
                    'last_active': last_activity.timestamp if last_activity else 'Never'
                })
        
        return lazy_members
    
    def __repr__(self):
        return f'<Project {self.name}>'

class ProjectMember(db.Model):
    __tablename__ = 'project_members'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure unique user-project pairs
    __table_args__ = (db.UniqueConstraint('user_id', 'project_id', name='unique_user_project'),)
    
    def __repr__(self):
        return f'<ProjectMember user={self.user_id} project={self.project_id}>'