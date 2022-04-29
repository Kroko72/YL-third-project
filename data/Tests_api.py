import flask
import flask_login
from flask import jsonify, render_template
from flask_login import current_user
from . import db_session
from .test import Test


blueprint = flask.Blueprint(
    'users_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/tests_api')
@flask_login.login_required
def get_users_by_grade():
    if current_user.admin:
        session = db_session.create_session()
        tests = session.query(Test).all()
        return jsonify({'tests': [item.to_dict(
            only=('id', 'title', "content", "images", 'grade', "grade_char")) for item in tests]})
    else:
        return render_template("error_page.html", title="Недостаточно прав", error_message="Недостаточно прав")
