from flask import Blueprint, render_template
from flask_login import login_required

games_bp = Blueprint('games', __name__)

@games_bp.route('/games')
@login_required
def games():
    return render_template('games.html')

@games_bp.route('/games/checkers')
@login_required
def checkers():
    return render_template('checkers.html')

@games_bp.route('/games/dice-cocktail')
@login_required
def dice_cocktail():
    return render_template('dice_cocktail.html')