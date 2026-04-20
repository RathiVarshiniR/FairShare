"""
Project management routes
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime

# Import db from extensions
from extensions import db
from models.user import User
from models.project import Project, ProjectMember
from models.task import Task

bp = Blueprint('projects', __name__)

@bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard showing user's projects and stats"""
    # Get projects where user is owner or member
    owned_projects = Project.query.filter_by(owner_id=current_user.id).all()
    member_projects = Project.query.join(ProjectMember).filter(
        ProjectMember.user_id == current_user.id
    ).all()
    
    # Combine and remove duplicates
    all_projects = list(set(owned_projects + member_projects))
    
    # Get lazy alerts for each project
    projects_with_alerts = []
    for project in all_projects:
        lazy_members = project.check_lazy_members()
        if lazy_members:
            projects_with_alerts.append({
                'project': project,
                'lazy_members': lazy_members
            })
    
    return render_template('projects/dashboard.html', 
                         projects=all_projects,
                         alerts=projects_with_alerts)

@bp.route('/list')
@login_required
def project_list():
    """Show all projects with creation date"""
    # Get projects where user is owner or member
    owned_projects = Project.query.filter_by(owner_id=current_user.id).all()
    member_projects = Project.query.join(ProjectMember).filter(
        ProjectMember.user_id == current_user.id
    ).all()
    
    # Combine and remove duplicates
    all_projects = list(set(owned_projects + member_projects))
    
    return render_template('projects/list.html', projects=all_projects)

@bp.route('/projects/create', methods=['GET', 'POST'])
@login_required
def create_project():
    """Create a new project"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        deadline_str = request.form.get('deadline')
        
        try:
            # Convert string to datetime object
            deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
        except (ValueError, TypeError):
            flash('Invalid date format. Please use YYYY-MM-DD', 'error')
            return render_template('projects/create.html')
        
        project = Project(
            name=name,
            description=description,
            deadline=deadline,
            owner_id=current_user.id
        )
        
        db.session.add(project)
        db.session.flush()  # Get project ID
        
        # Add owner as member
        project_member = ProjectMember(
            user_id=current_user.id,
            project_id=project.id
        )
        db.session.add(project_member)
        db.session.commit()
        
        flash('Project created successfully!', 'success')
        return redirect(url_for('projects.view_project', project_id=project.id))
    
    return render_template('projects/create.html')

@bp.route('/projects/<int:project_id>')
@login_required
def view_project(project_id):
    """View project details"""
    project = Project.query.get_or_404(project_id)
    
    # Check if user has access
    if not (project.owner_id == current_user.id or 
            ProjectMember.query.filter_by(project_id=project_id, user_id=current_user.id).first()):
        flash('You do not have access to this project', 'error')
        return redirect(url_for('projects.dashboard'))
    
    tasks = Task.query.filter_by(project_id=project_id).all()
    members_with_scores = project.get_members_with_scores()
    lazy_members = project.check_lazy_members()
    
    # Pass current datetime for deadline calculations
    now = datetime.utcnow()
    
    return render_template('projects/view.html',
                         project=project,
                         tasks=tasks,
                         members=members_with_scores,
                         lazy_members=lazy_members,
                         now=now)
@bp.route('/performance')
@login_required
def performance():
    """Show user's performance across all projects"""
    # Get projects where user is owner or member
    owned_projects = Project.query.filter_by(owner_id=current_user.id).all()
    member_projects = Project.query.join(ProjectMember).filter(
        ProjectMember.user_id == current_user.id
    ).all()
    
    all_projects = list(set(owned_projects + member_projects))
    
    return render_template('performance.html', projects=all_projects)
@bp.route('/notifications')
@login_required
def notifications():
    """Show user's notifications"""
    from models.notification import Notification
    
    notifications = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(Notification.created_at.desc()).all()
    
    # Mark as read
    for notification in notifications:
        notification.read = True
    db.session.commit()
    
    return render_template('notifications.html', notifications=notifications)

@bp.route('/projects/<int:project_id>/members/add', methods=['POST'])
@login_required
def add_member(project_id):
    """Add a member to the project"""
    project = Project.query.get_or_404(project_id)
    
    # Only owner can add members
    if project.owner_id != current_user.id:
        flash('Only project owner can add members', 'error')
        return redirect(url_for('projects.view_project', project_id=project_id))
    
    email = request.form.get('email')
    user = User.query.filter_by(email=email).first()
    
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('projects.view_project', project_id=project_id))
    
    # Check if already a member
    existing = ProjectMember.query.filter_by(
        project_id=project_id,
        user_id=user.id
    ).first()
    
    if existing:
        flash('User is already a member', 'warning')
        return redirect(url_for('projects.view_project', project_id=project_id))
    
    # Add member
    member = ProjectMember(user_id=user.id, project_id=project_id)
    db.session.add(member)
    db.session.commit()
    
    flash(f'{user.name} added to project', 'success')
    return redirect(url_for('projects.view_project', project_id=project_id))

@bp.route('/projects/<int:project_id>/members/remove/<int:user_id>', methods=['POST'])
@login_required
def remove_member(project_id, user_id):
    """Remove a member from the project"""
    project = Project.query.get_or_404(project_id)
    
    # Only owner can remove members
    if project.owner_id != current_user.id:
        flash('Only project owner can remove members', 'error')
        return redirect(url_for('projects.view_project', project_id=project_id))
    
    # Cannot remove yourself if you're the owner
    if user_id == current_user.id:
        flash('Cannot remove yourself as owner', 'error')
        return redirect(url_for('projects.view_project', project_id=project_id))
    
    member = ProjectMember.query.filter_by(
        project_id=project_id,
        user_id=user_id
    ).first_or_404()
    
    db.session.delete(member)
    db.session.commit()
    
    flash('Member removed from project', 'success')
    return redirect(url_for('projects.view_project', project_id=project_id))