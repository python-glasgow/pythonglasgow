from flask import Blueprint, render_template

from ug.util.cache import cached

mod = Blueprint('base', __name__)


@mod.route('/')
@cached(timeout=60 * 2)  # 2 mins
def index():
    return render_template('base/index.html')


@mod.route('/code-of-conduct/')
def code_of_conduct():
    return render_template('base/code_of_conduct.html')
