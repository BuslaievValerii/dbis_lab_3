from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import numpy as np
import math

NUM_OF_ENTRIES = 100

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/chess'
app.config['SECRET_KEY'] = "string"
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)


# ----------------------------------------------------------
# DATABASE LAYER (working only with database level)
# Creating entties

class Player(db.Model):
	__tablename__ = "player"
	player_id = db.Column(db.String(32), primary_key=True)
	player_rating = db.Column(db.Integer, nullable=False)

	def __init__(self, id, rating):
		self.player_id = id
		self.player_rating = rating


class Increment(db.Model):
	__tablename__ = "increment"
	increment_code = db.Column(db.String(8), primary_key=True)

	def __init__(self, code):
		self.increment_code = code


class Opening(db.Model):
	__tablename__ = "opening"
	opening_name = db.Column(db.String(128), primary_key=True)

	def __init__(self, name):
		self.opening_name = name


class Game(db.Model):
	__tablename__ = "game"
	id = db.Column(db.String(8), primary_key=True)
	rated = db.Column(db.Boolean, nullable=False)
	created_at = db.Column(db.Float, nullable=False)
	last_move_at = db.Column(db.Float, nullable=False)
	turns = db.Column(db.Integer, nullable=False)
	victory_status = db.Column(db.String(16), nullable=False)
	winner = db.Column(db.String(8), nullable=False)
	increment_code = db.Column(db.String(8), db.ForeignKey("increment.increment_code"), nullable=False)
	white_id = db.Column(db.String(32), db.ForeignKey("player.player_id"), nullable=False)
	black_id = db.Column(db.String(32), db.ForeignKey("player.player_id"), nullable=False)
	moves = db.Column(db.String(2048), nullable=False)
	opening_name = db.Column(db.String(128), db.ForeignKey("opening.opening_name"), nullable=False)
	opening_ply = db.Column(db.Integer, nullable=False)

	white_rating = db.relationship("Player", lazy="joined", backref="games", uselist=False, foreign_keys=[white_id])
	white_rating = db.relationship("Player", lazy="joined", backref="games", uselist=False, foreign_keys=[black_id])

	def __init__(self, id, rated, created_at, last_move_at, turns, victory_status, winner, increment_code, white_id, black_id, moves, opening_name, opening_ply):
		self.id = id
		self.rated = rated
		self.created_at = created_at
		self.last_move_at = last_move_at
		self.turns = turns
		self.victory_status = victory_status
		self.winner = winner
		self.increment_code = increment_code
		self.white_id = white_id
		self.black_id = black_id
		self.moves = moves
		self.opening_name = opening_name
		self.opening_ply = opening_ply
# ----------------------------------------------------------

# ----------------------------------------------------------
# 

@app.route('/insert', methods=['GET','POST'])
def insert():
	data = pd.read_csv('games.csv')
	data = data.to_numpy()
	for row in data:
		white_id = row[8]
		white_rating = row[9]
		player = Player.query.filter_by(player_id=white_id).first()
		if player is None:
			player = Player(white_id, white_rating)
			db.session.add(player)
		else:
			player.player_rating = white_rating
		db.session.commit()

		black_id = row[10]
		black_rating = row[11]
		player = Player.query.filter_by(player_id=black_id).first()
		if player is None:
			player = Player(black_id, black_rating)
			db.session.add(player)
		else:
			player.player_rating = black_rating
		db.session.commit()

		increment_code = row[7]
		increment = Increment.query.filter_by(increment_code=increment_code).first()
		if increment is None:
			increment = Increment(increment_code)
			db.session.add(increment)
		db.session.commit()

		opening_name = row[14]
		opening = Opening.query.filter_by(opening_name=opening_name).first()
		if opening is None:
			opening = Opening(opening_name)
			db.session.add(opening)
		db.session.commit()

		id = row[0]
		game = Game.query.filter_by(id=id).first()
		if game is None:
			game = Game(id, row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[10], row[12], row[14], row[15])
			db.session.add(game)
		db.session.commit()
	return redirect(url_for('index'))


@app.route('/')
def index():
	return render_template('index.html')

@app.route('/player/<int:page>')
def show_players(page=1):
	start = (page-1) * NUM_OF_ENTRIES
	end = page * NUM_OF_ENTRIES
	last_page = math.ceil(Player.query.count() / NUM_OF_ENTRIES)
	return render_template('show_players.html', players=Player.query[start:end], last_page=last_page)

@app.route('/increment/<int:page>')
def show_increment(page=1):
	start = (page-1) * NUM_OF_ENTRIES
	end = page * NUM_OF_ENTRIES
	last_page = math.ceil(Increment.query.count() / NUM_OF_ENTRIES)
	return render_template('show_increment.html', increments=Increment.query[start:end], last_page=last_page)

@app.route('/opening/<int:page>')
def show_opening(page=1):
	start = (page-1) * NUM_OF_ENTRIES
	end = page * NUM_OF_ENTRIES
	last_page = math.ceil(Opening.query.count() / NUM_OF_ENTRIES)
	return render_template('show_opening.html', openings=Opening.query[start:end], last_page=last_page)


@app.route('/game/<int:page>')
def show_games(page=1):
	start = (page-1) * NUM_OF_ENTRIES
	end = page * NUM_OF_ENTRIES
	last_page = math.ceil(Game.query.count() / NUM_OF_ENTRIES)
	return render_template('show_games.html', games=Game.query[start:end], last_page=last_page)



@app.route('/player/add_player', methods=['GET', 'POST'])
def add_player():
	if request.method == 'POST':
		if not request.form['player_id'] or not request.form['player_rating']:
			flash('Please, enter all the fields', 'Error')
		elif Player.query.filter_by(player_id=request.form['player_id']).first() is not None:
			try:
				rating = int(request.form['player_rating'])
				player = Player.query.filter_by(player_id=request.form['player_id']).first()
				db.session.delete(player)
				player.player_rating = rating
				db.session.add(player)
			except:
				flash('Something went wrong. Check input data', 'Error')
			db.session.commit()
		else:
			try:
				rating = int(request.form['player_rating'])
				player = Player(request.form['player_id'], request.form['player_rating'])
				try:
					db.session.add(player)
					db.session.commit()
					last_page = math.ceil(Player.query.count() / NUM_OF_ENTRIES)
					return redirect(url_for('show_players', page=last_page))
				except:
					flash('Failed to insert your data', 'Error')
			except:
				flash('Something went wrong. Check input data', 'Error')
		return redirect(url_for('add_player'))

	return render_template('add_player.html')

@app.route('/player/delete', methods=['POST'])
def delete_player():
	player_id = request.form['player_id']
	player = Player.query.filter_by(player_id=player_id).first()
	while Game.query.filter_by(white_id=player_id).first() is not None:
		db.session.delete(Game.query.filter_by(white_id=player_id).first())
	while Game.query.filter_by(black_id=player_id).first() is not None:
		db.session.delete(Game.query.filter_by(black_id=player_id).first())
	db.session.delete(player)
	db.session.commit()
	return redirect(url_for('show_players', page=1))


@app.route('/game/add_game', methods=['GET', 'POST'])
def add_game():
	if request.method == 'POST':
		rated = request.form.get('rated', False) == 'rated'

		if not request.form['id'] or not request.form['rated'] or not request.form['created_at'] or not request.form['last_move_at'] or not request.form['turns'] or not request.form['victory_status'] or not request.form['winner'] or not request.form['increment_code'] or not request.form['white_id'] or not request.form['black_id'] or not request.form['moves'] or not request.form['opening_name'] or not request.form['opening_ply']:
			flash('Please, enter all the fields', 'Error')
		elif Player.query.filter_by(player_id=request.form['white_id']).first() is None:
			flash('The person who you chose as a white player does not exist in the database', 'Error')
		elif Player.query.filter_by(player_id=request.form['black_id']).first() is None:
			flash('The person who you chose as a black player does not exist in the database', 'Error')
		elif Increment.query.filter_by(increment_code=request.form['increment_code']).first() is None:
			flash('No such increment code in database', 'Error')
		elif Opening.query.filter_by(opening_name=request.form['opening_name']).first() is None:
			flash('No such opening name code in database', 'Error')
		elif Game.query.filter_by(id=request.form['id']).first() is not None:
			flash('Game with such id already exists', 'Error')
		else:
			try:

				game = Game(request.form['id'], request.form['rated'], request.form['created_at'], request.form['last_move_at'], request.form['turns'], request.form['victory status'], request.form['winner'], request.form['increment_code'], request.form['white_id'], request.form['black_id'], request.form['moves'], request.form['opening_name'], request.form['opening_ply'])
				try:
					db.session.add(game)
					db.session.commit()
					last_page = math.ceil(Game.query.count() / NUM_OF_ENTRIES)
					return redirect(url_for('show_games', page=last_page))
				except:
					flash('Failed to insert your data', 'Error')
			except:
				flash('Something went wrong. Check input data', 'Error')
		return redirect(url_for('add_game'))

	return render_template('add_game.html')

@app.route('/game/delete', methods=['POST'])
def delete_game():
	id = request.form['id']
	game = Player.query.filter_by(id=id).first()
	db.session.delete(game)
	db.session.commit()
	return redirect(url_for('show_games', page=1))


if __name__ == '__main__':
	db.create_all()
	app.run(debug=True)
