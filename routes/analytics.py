"""
Analytics routes
"""

from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from models.user import User
from models.project import Project, ProjectMember
from models.task import Task
from models.activity import ActivityLog
from datetime import datetime, timedelta

bp = Blueprint('analytics', __name__, url_prefix='/analytics')

@bp.route('/project/<int:project_id>')
@login_required
def project_analytics(project_id):
    """View analytics for a project"""
    project = Project.query.get_or_404(project_id)
    
    # Check access
    if not (project.owner_id == current_user.id or 
            ProjectMember.query.filter_by(project_id=project_id, user_id=current_user.id).first()):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get all tasks
    tasks = Task.query.filter_by(project_id=project_id).all()
    
    # Task statistics
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t.status == 'completed')
    in_progress_tasks = sum(1 for t in tasks if t.status == 'in_progress')
    not_started_tasks = sum(1 for t in tasks if t.status == 'not_started')
    
    # Priority breakdown
    priority_counts = {
        'low': sum(1 for t in tasks if t.priority == 'low'),
        'medium': sum(1 for t in tasks if t.priority == 'medium'),
        'high': sum(1 for t in tasks if t.priority == 'high')
    }
    
    # Activity timeline (last 7 days)
    timeline = []
    for i in range(6, -1, -1):
        day = datetime.utcnow() - timedelta(days=i)
        next_day = day + timedelta(days=1)
        
        count = ActivityLog.query.filter(
            ActivityLog.project_id == project_id,
            ActivityLog.timestamp >= day,
            ActivityLog.timestamp < next_day
        ).count()
        
        timeline.append({
            'date': day.strftime('%Y-%m-%d'),
            'count': count
        })
    
    # Member performance
    members = project.get_members_with_scores()
    
    stats = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'in_progress_tasks': in_progress_tasks,
        'not_started_tasks': not_started_tasks,
        'completion_rate': round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1),
        'priority_breakdown': priority_counts,
        'timeline': timeline,
        'members': members
    }
    
    return render_template('analytics/project.html', 
                         project=project, 
                         stats=stats)

@bp.route('/project/<int:project_id>/data')
@login_required
def project_data(project_id):
    """Return JSON data for charts"""
    project = Project.query.get_or_404(project_id)
    
    # Check access
    if not (project.owner_id == current_user.id or 
            ProjectMember.query.filter_by(project_id=project_id, user_id=current_user.id).first()):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get tasks by member
    members = User.query.join(ProjectMember).filter(
        ProjectMember.project_id == project_id
    ).all()
    
    member_data = []
    for member in members:
        member_tasks = Task.query.filter_by(
            project_id=project_id,
            assigned_to=member.id
        ).all()
        
        completed = sum(1 for t in member_tasks if t.status == 'completed')
        total = len(member_tasks)
        
        member_data.append({
            'name': member.name,
            'completed': completed,
            'total': total,
            'score': member.get_fairness_score(project_id)['score']
        })
    
    # Activity over time
    activities = ActivityLog.query.filter_by(project_id=project_id).all()
    activity_by_day = {}
    
    for activity in activities:
        day = activity.timestamp.strftime('%Y-%m-%d')
        activity_by_day[day] = activity_by_day.get(day, 0) + 1
    
    timeline = [{'date': d, 'count': c} for d, c in sorted(activity_by_day.items())]
    
    return jsonify({
        'member_performance': member_data,
        'timeline': timeline
    })