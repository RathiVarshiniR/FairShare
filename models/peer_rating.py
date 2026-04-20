"""
PeerRating model for team member evaluations
"""

from extensions import db
from datetime import datetime

class PeerRating(db.Model):
    __tablename__ = 'peer_ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    rater_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rated_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure one rating per rater-rated-project combination
    __table_args__ = (
        db.UniqueConstraint('rater_id', 'rated_user_id', 'project_id', 
                           name='unique_rating_per_project'),
    )
    
    def validate_rating(self):
        """Validate rating is between 1 and 5"""
        return 1 <= self.rating <= 5
    
    def __repr__(self):
        return f'<PeerRating from {self.rater_id} to {self.rated_user_id}: {self.rating}>'