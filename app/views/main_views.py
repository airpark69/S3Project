import csv

from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)


@main_bp.route('/', methods=['GET'])
@main_bp.route('/index.html', methods=['GET'])
def index():
   
  return render_template('index.html'), 200

@main_bp.route('/generic.html', methods=['GET'])
def generic():
   
  return render_template('generic.html'), 200

@main_bp.route('/elements.html', methods=['GET'])
def elements():
   
  return render_template('elements.html'), 200

