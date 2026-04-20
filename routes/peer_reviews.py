"""
Peer review routes
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user

# Import db from extensions instead of app
from extensions import db
from models.user import User
from models.project import Project, ProjectMember
from models.peer_rating import PeerRating

bp = Blueprint('peer_reviews', __name__, url_prefix='/reviews')

@bp.route('/project/<int:project_id>')
@login_required
def project_reviews(project_id):
    """View peer reviews for a project"""
    project = Project.query.get_or_404(project_id)
    
    # Check access
    if not (project.owner_id == current_user.id or 
            ProjectMember.query.filter_by(project_id=project_id, user_id=current_user.id).first()):
        flash('You do not have access to this project', 'error')
        return redirect(url_for('projects.dashboard'))
    
    # Get all members
    members = User.query.join(ProjectMember).filter(
        ProjectMember.project_id == project_id
    ).all()
    
    # Get existing ratings by current user
    existing_ratings = {
        r.rated_user_id: r for r in PeerRating.query.filter_by(
            project_id=project_id,
            rater_id=current_user.id
        ).all()
    }
    
    # Get all ratings for each member
    member_ratings = {}
    for member in members:
        ratings = PeerRating.query.filter_by(
            project_id=project_id,
            rated_user_id=member.id
        ).all()
        if ratings:
            avg_rating = sum(r.rating for r in ratings) / len(ratings)
            member_ratings[member.id] = {
                'average': round(avg_rating, 1),
                'count': len(ratings)
            }
    
    return render_template('reviews/project.html',
                         project=project,
                         members=members,
                         existing_ratings=existing_ratings,
                         member_ratings=member_ratings)

@bp.route('/rate', methods=['POST'])
@login_required
def rate_member():
    """Rate a team member"""
    data = request.get_json()
    
    project_id = data.get('project_id')
    rated_user_id = data.get('rated_user_id')
    rating = data.get('rating')
    comment = data.get('comment', '')
    
    # Validate
    if rated_user_id == current_user.id:
        return jsonify({'error': 'Cannot rate yourself'}), 400
    
    if not (1 <= rating <= 5):
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400
    
    # Check if both users are in the project
    Project.query.get_or_404(project_id)  # ensure project exists
    members = ProjectMember.query.filter_by(project_id=project_id).all()
    member_ids = [m.user_id for m in members]
    
    if current_user.id not in member_ids or rated_user_id not in member_ids:
        return jsonify({'error': 'Users must be project members'}), 400
    
    # Check for existing rating
    existing = PeerRating.query.filter_by(
        project_id=project_id,
        rater_id=current_user.id,
        rated_user_id=rated_user_id
    ).first()
    
    if existing:
        # Update existing rating
        existing.rating = rating
        existing.comment = comment
    else:
        # Create new rating
        peer_rating = PeerRating(
            rater_id=current_user.id,
            rated_user_id=rated_user_id,
            project_id=project_id,
            rating=rating,
            comment=comment
        )
        db.session.add(peer_rating)
    
    db.session.commit()
    
    return jsonify({'success': True})