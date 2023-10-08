from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()

DB_NAME = "travel"
DB_PASSWORD = ''           
DB_HOST = 'localhost'           
DB_PORT = '3306'         
DB_USERNAME= 'root'


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'asaaddsfsdgfdgfgfxd'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    db.init_app(app)
    
    from .views import views
    from .auth import auth
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    from .models import Agency
    
    create_database(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(agency_id):
        return Agency.query.get(int(agency_id))
    
    return app



def create_database(app):
    if not path.exists('app/'+ DB_NAME):
        db.create_all(app=app)
        print('Database Created')
 
 
        
if __name__ == '__main__':
    app = create_app()
    
    db_file_path = path.join(app.root_path, f'{DB_NAME}.db')
    if not path.exists(db_file_path):
        with app.app_context():
            db.create_all()
        print('Database Created')
    
    app.run(debug=True)
