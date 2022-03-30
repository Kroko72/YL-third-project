import flask
import flask_login
from flask import jsonify, render_template
from flask_login import current_user
from data import db_session
from data.users import User


blueprint = flask.Blueprint(
    'users_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/users/<int:grade>')
@flask_login.login_required
def get_users_by_grade(grade):
    if current_user.id == 1:
        session = db_session.create_session()
        user = session.query(User).filter(User.grade == int(grade)).all()
        return jsonify({'users': [item.to_dict(
            only=('surname', 'name', 'grade', "grade_char", "email")) for item in user]})
    else:
        return render_template("error_page.html", title="Недостаточно прав", error_message="Недостаточно прав")