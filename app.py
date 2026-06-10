from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fairshare.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Register blueprints
    from routes.auth import auth
    from routes.projects import projects
    from routes.tasks import tasks
    from routes.analytics import analytics
    from routes.peer_reviews import peer_reviews

    app.register_blueprint(auth)
    app.register_blueprint(projects)
    app.register_blueprint(tasks)
    app.register_blueprint(analytics)
    app.register_blueprint(peer_reviews)

    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
