import json
from flask import Flask, redirect, url_for, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
#import subprocess

app = Flask(__name__)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///playlists.db"

db = SQLAlchemy(app)

class Song(db.Model):
	songid = db.Column(db.Integer, primary_key = True)
	song_name = db.Column(db.String(100))
	artist = db.Column(db.String(100))
	genre = db.Column(db.String(100))

class Playlist(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(100))
	songid = db.Column(db.Integer)

@app.route("/", methods = ["POST", "GET"])
def home():
	return render_template('home.html')

@app.route("/songs/<playlist_name>", methods = ["POST", "GET"])
def songs_page(playlist_name):
	p_objects = Playlist.query.filter_by(name = playlist_name)
	songid_list = [p.songid for p in p_objects]
	s_objects = Song.query.filter(Song.songid.in_(songid_list))
	song_names = [p.song_name for p in s_objects]
	return render_template('songs.html', songs = song_names, playlist_name = playlist_name)

@app.route("/playlists", methods = ["POST", "GET"])
def playlist_page():
	if request.method == 'POST':
		playlist_name = request.form['playlist_name']
		selected_songs = request.form.getlist('selected-songs')
		print(selected_songs)
		s_objects = Song.query.filter(Song.song_name.in_(selected_songs))
		song_ids = [p.songid for p in s_objects]
		print(song_ids)
		for song_id in song_ids:
			entry = Playlist(name = playlist_name, songid = song_id)
			db.session.add(entry)
		db.session.commit()

	query_distinct = Playlist.query.with_entities(Playlist.name).distinct()
	distinct_playlists = [r.name for r in query_distinct]
	return render_template('playlists.html', playlists = distinct_playlists)

@app.route("/allsongs", methods = ["POST", "GET"])
def all_songs_page():
	s_objects = Song.query.all()
	song_names = [p.song_name for p in s_objects]
	return render_template('all_songs.html', songs = song_names)

@app.route("/playsong/<song_name>", methods = ["POST", "GET"])
def music_player(song_name):
	path = os.path.join('music', song_name)
	print(path)
	return render_template('play_song.html', song_name = song_name, path = path)

@app.route("/addsong/<playlist_name>", methods = ["POST", "GET"])
def add_songs_playlist(playlist_name):
	if request.method == 'POST':
		playlist_name = request.form['playlist_name']
		print(playlist_name)

	s_objects = Song.query.all()
	all_song_names = [p.song_name for p in s_objects]

	p_objects = Playlist.query.filter_by(name = playlist_name)
	songid_list = [p.songid for p in p_objects]
	s_objects = Song.query.filter(Song.songid.in_(songid_list))
	song_names_playlist = [p.song_name for p in s_objects]

	songs_for_playlist = list(set(all_song_names) - set(song_names_playlist))
	print(songs_for_playlist)
	return render_template('add_songs.html', songs = songs_for_playlist, playlist_name = playlist_name)

if __name__ == "__main__":
	app.run(port=5000, debug = True)
