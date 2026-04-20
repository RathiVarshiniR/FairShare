"""
Task management routes
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models.user import User
from models.project import Project, ProjectMember
from models.task import Task
from datetime import datetime

bp = Blueprint('tasks', __name__, url_prefix='/tasks')

@bp.route('/create/<int:project_id>', methods=['GET', 'POST'])
@login_required
def create_task(project_id):
    """Create a new task in a project"""
    project = Project.query.get_or_404(project_id)
    
    # Check if user is a member
    if not (project.owner_id == current_user.id or 
            ProjectMember.query.filter_by(project_id=project_id, user_id=current_user.id).first()):
        flash('You do not have access to this project', 'error')
        return redirect(url_for('projects.dashboard'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        assigned_to = request.form.get('assigned_to')
        deadline_str = request.form.get('deadline')
        priority = request.form.get('priority', 'medium')
        
        try:
            deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format', 'error')
            return render_template('tasks/create.html', project=project)
        
        task = Task(
            title=title,
            description=description,
            assigned_to=assigned_to,
            deadline=deadline,
            priority=priority,
            project_id=project_id
        )
        
        db.session.add(task)
        db.session.commit()
        
        flash('Task created successfully!', 'success')
        return redirect(url_for('projects.view_project', project_id=project_id))
    
    # Get project members for assignment dropdown
    members = User.query.join(ProjectMember).filter(
        ProjectMember.project_id == project_id
    ).all()
    
    return render_template('tasks/create.html', project=project, members=members)

@bp.route('/<int:task_id>')
@login_required
def view_task(task_id):
    """View task details"""
    task = Task.query.get_or_404(task_id)
    
    # Check access
    project = Project.query.get(task.project_id)
    if not (project.owner_id == current_user.id or 
            ProjectMember.query.filter_by(project_id=task.project_id, user_id=current_user.id).first()):
        flash('You do not have access to this task', 'error')
        return redirect(url_for('projects.dashboard'))
    
    return render_template('tasks/view.html', task=task)

@bp.route('/<int:task_id>/update-progress', methods=['POST'])
@login_required
def update_progress(task_id):
    """Update task progress"""
    task = Task.query.get_or_404(task_id)
    
    # Only assigned user can update progress
    if task.assigned_to != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    progress = data.get('progress', 0)
    
    task.update_progress(progress)
    
    return jsonify({
        'success': True,
        'progress': task.progress,
        'status': task.status
    })

@bp.route('/<int:task_id>/update-status', methods=['POST'])
@login_required
def update_status(task_id):
    """Update task status"""
    task = Task.query.get_or_404(task_id)
    
    # Check if user can update (assigned or owner)
    project = Project.query.get(task.project_id)
    if task.assigned_to != current_user.id and project.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    status = data.get('status')
    
    task.update_status(status)
    
    return jsonify({
        'success': True,
        'status': task.status
    })