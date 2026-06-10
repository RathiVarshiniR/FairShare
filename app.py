from flask import Flask, render_template
from extensions import db, login_manager
import os

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fairshare.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Register blueprints
    from routes.auth import bp as auth
    from routes.projects import bp as projects
    from routes.tasks import bp as tasks
    from routes.analytics import bp as analytics
    from routes.peer_reviews import bp as peer_reviews

    app.register_blueprint(auth)
    app.register_blueprint(projects)
    app.register_blueprint(tasks)
    app.register_blueprint(analytics)
    app.register_blueprint(peer_reviews)

    @app.route('/')
    def index():
        return render_template('index.html')

    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
