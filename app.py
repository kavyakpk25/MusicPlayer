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
class Recommended_playlist(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(100))
	songid = db.Column(db.Integer)

#def rec(db,song_name):




@app.route("/", methods = ["POST", "GET"])
def home():
	return render_template('home.html')

@app.route("/playsong/<song_name>", methods = ["POST", "GET"])
def music_player(song_name):
	s_objects = Song.query.all()
	song_names = [p.song_name for p in s_objects]
	artist_names = [p.artist for p in s_objects]
	path = os.path.join('music', song_name)
	#rec(db,song_name)
	
	r_objects = Recommended_playlist.query.all()
	s = Song.query.filter_by(song_name = song_name) #need to query with song id
	song_id=s[0].songid

	current = Song.query.filter_by(songid = song_id)

	current=list(current)[0]
	#print("current",current)

	p_objects=Song.query.all()
	metric = dict()
	#print("p_objects",p_objects)
	for i in p_objects:
		if i.songid != song_id:
			score=0
			score=int(i.artist == current.artist) + int(i.genre == current.genre)
			metric[i.songid]=score
	
	metric=dict(sorted(metric.items(), key=lambda item: item[1],reverse=True))
	print("Metric: ",metric)
	print(r_objects)
	if len(list(r_objects)) == 0:
		final= [i[0] for i in list(metric.items())[:5]]
		#print("HEREEE",final)
		p_objects = Song.query.filter(Song.songid.in_(final))
		#print("PPPPPPPPPPPPPPPP",list(p_objects))
		i=1
		for p in p_objects:
			entry = Recommended_playlist(id = i,name = p.song_name,songid=p.songid)
			db.session.add(entry)
			i+=1
		db.session.commit()

	else:
		l=list(metric.items())
		final=[x[0] for x in l[:5]]
		j=1
		p_objects = Song.query.filter(Song.songid.in_(final))
		for i in p_objects:
			instance = Recommended_playlist.query.filter(Recommended_playlist.id == j)
			d={"name":i.song_name,"songid":i.songid}
			instance.update(d)
			j+=1
			db.session.commit()



	return render_template('play_song.html',songs = song_names,artists=artist_names,song_name = song_name,path=path)


@app.route("/playsong/<playlist_name>/<song_name>", methods = ["POST", "GET"])
def music_player_playlist(song_name,playlist_name):
	p_objects = Playlist.query.filter_by(name = playlist_name)
	songid_list = [p.songid for p in p_objects]
	s_objects = Song.query.filter(Song.songid.in_(songid_list))
	song_names = [p.song_name for p in s_objects]
	artist_names = [p.artist for p in s_objects]
	path = os.path.join('music', song_name)

	r_objects = Recommended_playlist.query.all()
	s = Song.query.filter_by(song_name = song_name)
	song_id=s[0].songid

	current = Song.query.filter_by(songid = song_id)

	current=list(current)[0]
	#print("current",current)

	p_objects=Song.query.all()
	metric = dict()
	print("p_objects",p_objects)
	for i in p_objects:
		if i.songid != song_id:
			score=0
			score=int(i.artist == current.artist) + int(i.genre == current.genre)
			metric[i.songid]=score
	
	metric=dict(sorted(metric.items(), key=lambda item: item[1],reverse=True))
	print("Metric",metric)

	#print(r_objects)
	if len(list(r_objects)) == 0:
		final= [i[0] for i in list(metric.items())[:5]]
		#print("HEREEE",final)
		p_objects = Song.query.filter(Song.songid.in_(final))
		#print("PPPPPPPPPPPPPPPP",list(p_objects))
		i=1
		for p in p_objects:
			entry = Recommended_playlist(id = i,name = p.song_name,songid=p.songid)
			db.session.add(entry)
			i+=1
		db.session.commit()

	else:
		l=list(metric.items())
		final=[x[0] for x in l[:5]]
		j=1
		p_objects = Song.query.filter(Song.songid.in_(final))
		for i in p_objects:
			instance = Recommended_playlist.query.filter(Recommended_playlist.id == j)
			d={"name":i.song_name,"songid":i.songid}
			instance.update(d)
			j+=1
			db.session.commit()
	return render_template('play_song.html',songs = song_names,artists=artist_names,song_name = song_name,path=path)

@app.route("/playsong/recommendations/<song_name>", methods = ["POST", "GET"])
def music_player_recommender(song_name):
	r= Recommended_playlist.query.all()
	#p_objects = Playlist.query.filter_by(name = playlist_name)
	songid_list = [p.songid for p in r]
	s_objects = Song.query.filter(Song.songid.in_(songid_list))
	song_names = [p.name for p in r]
	artist_names = [p.artist for p in s_objects]
	path = os.path.join('music', song_name)
	#rec(db.model,song_name)
	return render_template('play_song.html',songs = song_names,artists=artist_names,song_name = song_name,path=path)

@app.route("/songs/<playlist_name>", methods = ["POST", "GET"])
def songs_page(playlist_name):
    p_objects = Playlist.query.filter_by(name = playlist_name)
    songid_list = [p.songid for p in p_objects]
    s_objects = Song.query.filter(Song.songid.in_(songid_list))
    return render_template('songs.html', songs = s_objects, playlist_name = playlist_name)

@app.route("/playlists", methods = ["POST", "GET"])
def playlist_page():
	if request.method == 'POST':
		playlist_name = request.form['playlist_name']
		selected_songs = request.form.getlist('selected-songs')

		print(selected_songs)
		s_objects = Song.query.filter(Song.songid.in_(selected_songs))
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
    if request.method == 'POST':
        print("HI POST OF ALL SONGS")
        song_name = request.form['song_name']
        print(song_name)
        return render_template('all_songs.html', songs = ['a', 'b'])
    else:
        s_objects = Song.query.all()
        # song_names = [p.song_name for p in s_objects]
        return render_template('all_songs.html', songs = s_objects)

@app.route("/recommendations", methods = ["POST", "GET"])
def recommendations():
	r= Recommended_playlist.query.all()
	r=[i.songid for i in r]
	s_objects = Song.query.filter(Song.songid.in_(r))
	return render_template('recommendations.html', songs = s_objects)

# @app.route("/playsong/<song_name>", methods = ["POST", "GET"])
# def music_player(song_name):
# 	path = os.path.join('music', song_name)
# 	print(path)
# 	return render_template('play_song.html', song_name = song_name, path = path)

@app.route("/addsong/<playlist_name>", methods = ["POST", "GET"])
def add_songs_playlist(playlist_name):
	if request.method == 'POST':
		playlist_name = request.form['playlist_name']
		print(playlist_name)

		query_distinct = Playlist.query.with_entities(Playlist.name).distinct()
		distinct_playlists = [r.name for r in query_distinct]

		if(playlist_name in distinct_playlists):
			message="This playlist already exists, please enter another name."
			return render_template('playlists.html', playlists = distinct_playlists,message=message)
		if(len(playlist_name)>32 or (playlist_name.isalnum())==False):
			message="Please enter an alphanumeric name < 32 characters."
			return render_template('playlists.html', playlists = distinct_playlists,message=message)
        #check for duplicate here
	s_objects = Song.query.all()
	all_song_names = [p.song_name for p in s_objects]
	all_song_ids = [p.songid for p in s_objects]

	p_objects = Playlist.query.filter_by(name = playlist_name)
	songid_list = [p.songid for p in p_objects]

	#song_names_playlist = [p.song_name for p in s_objects]

	songsid_for_playlist = list(set(all_song_ids) - set(songid_list))
	s_objects = Song.query.filter(Song.songid.in_(songsid_for_playlist))
	print([s.song_name for s in s_objects])
	#songs_for_playlist = list(set(all_song_names) - set(song_names_playlist))
	#print(songs_for_playlist)
	return render_template('add_songs.html', songs = s_objects, playlist_name = playlist_name)

@app.route("/playlistsongs/delete/<int:songid>", methods = ["POST", "GET"])
def delete_song_from_playlist(songid):
    songs_playlist = Playlist.query.filter_by(songid = songid).all()
    print(len(songs_playlist))
    playlist_name = songs_playlist[0].name
    print(songs_playlist[0].name)
    db.session.delete(songs_playlist[0])
    db.session.commit()
    return redirect(url_for('songs_page', playlist_name = playlist_name))

@app.route("/delete/<playlist_name>", methods = ["POST", "GET"])
def delete_playlist(playlist_name):
    p_objects = Playlist.query.filter_by(name = playlist_name)
    for p in p_objects:
        print(p.name)
        print(p.songid)
        print()
        db.session.delete(p)
    db.session.commit()
    query_distinct = Playlist.query.with_entities(Playlist.name).distinct()
    distinct_playlists = [r.name for r in query_distinct]
    print(distinct_playlists)
    return redirect(url_for('playlist_page'))

@app.route("/allsongs/delete/<int:songid>", methods = ["POST", "GET"])
def delete_song_from_all_songs(songid):
    song = Song.query.get_or_404(songid)
    print(song.song_name)
    db.session.delete(song)
    db.session.commit()
    print("P")
    songs_playlist = Playlist.query.filter_by(songid = songid)
    for s in songs_playlist:
        print(s.name)
        db.session.delete(s)
    db.session.commit()
    return redirect('/allsongs')

if __name__ == "__main__":
	app.run(port=5000, debug = True)
