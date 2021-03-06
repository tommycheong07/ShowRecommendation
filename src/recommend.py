from database import *

# baseGenreList = ['Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 
# 'Documentary', 'Drama', 'Family', 'Fantasy', 'Game Show', 'History', 'Horror', 'Music', 
# 'Musical', 'Mystery', 'News', 'Reality-TV', 'Romance', 'Sci-Fi', 'Sport', 'Superhero', 
# 'Talk Show', 'Thriller', 'War', 'Western']



def appendGenreAndPrint(moviesQ, recMoviesQ, recReason):
	print("##### ")
	print("*** Based on your criterias, we suggest these movies: ***")

	movieDictionary = {}
	movieDictionary["Selection"] = []
	movieDictionary["Recommendation"] = []
	

	for row in moviesQ:
		genres = []
		genres_q = (MovieGenre.select().where(MovieGenre.movieID == row.movieID))

		for genre in genres_q:
			genres.append(genre.genre)

		movieDictionary["Selection"].append({'movie': row.movie, 'summary': row.summary, 'rating': row.rating, 'genres': genres})

		# print("Title: " + row.movie, "\nSummary: " + row.summary, "\nRating: " + row.rating, "\nGenres: ", genres)
		# print("\n")

	# print("*** We also recommend these movies that you may be interested in based on other actors/actresses " + 
	# 	"who have played in movies ` selected actor/actress or similar genres.: ***\n")

	for row in recMoviesQ:
		genres = []
		genres_q = (MovieGenre.select().where(MovieGenre.movieID == row.movieID))
		reason = ""

		for genre in genres_q:
			genres.append(genre.genre)

		actors_q = (ActorMovie.select().where(ActorMovie.movieID == row.movieID))
		for actor in actors_q:
			for key in recReason:
				if actor.nm == key:
					reason = actor.actorName + " has been in " + str(recReason.get(key)) + " movies with your selected actor/actress"

		movieDictionary["Recommendation"].append({'movie': row.movie, 'summary': row.summary, 'rating': row.rating, 'genres': genres, 'reason': reason})

	return movieDictionary

		# print("Title: " + row.movie, "\nSummary: " + row.summary, "\nRating: " + row.rating, "\nGenres: ", genres)
		# print("\n")


def searchByGenres(genres):
	movies_q = (MovieGenre.select().join(Movie, on=(Movie.movieID == MovieGenre.movieID)).where(MovieGenre.genre.in_(genres)).order_by(Movie.rating.desc()).limit(1000))

	movieIDList = []

	for row in movies_q:
		movieIDList.append(row.movieID)

	movieInfo_q = (Movie.select().where(Movie.movieID.in_(movieIDList)).order_by(Movie.rating.desc()).limit(10))

	rec_movies_q, rec_reason = recByGenres(movieIDList, genres)

	return appendGenreAndPrint(movieInfo_q, rec_movies_q, rec_reason)

def searchByActors(actorNames):
	actor_q = (ActorMovie.select().where(ActorMovie.actorName.in_(actorNames)))

	actorMovieList = []

	for row in actor_q:
		actorMovieList.append(row.movieID)


	movies_q = (Movie.select().where(Movie.movieID.in_(actorMovieList)).order_by(Movie.rating.desc()).limit(10))

	recommend_movies_q, rec_reason = recByActors(actorNames, actorMovieList)

	return appendGenreAndPrint(movies_q, recommend_movies_q, rec_reason)

def search(actorNames, genres):
	movies_q = (MovieGenre.select().where(MovieGenre.genre.in_(genres)))

	genreMovieList = []

	for row in movies_q:
		genreMovieList.append(row.movieID)


	actor_q = (ActorMovie.select().where(ActorMovie.actorName.in_(actorNames)))

	actorMovieList = []

	for row in actor_q:
		actorMovieList.append(row.movieID)

	mov_q = (Movie.select().where((Movie.movieID.in_(actorMovieList)) & (Movie.movieID.in_(genreMovieList))))

	movList = []

	for row in mov_q:
		movList.append(row.movieID)

	movieInfo_q = (Movie.select().where(Movie.movieID.in_(movList)).order_by(Movie.rating.desc()).limit(10))

	rec_movies_q, rec_reason = recSearch(actorNames, movList, genres)

	return appendGenreAndPrint(movieInfo_q, rec_movies_q, rec_reason)

def recByActors(actorNamesList, movieList):
	otherActors = (ActorMovie.select(ActorMovie.nm, fn.COUNT(ActorMovie.nm).alias('count'))
								.where((ActorMovie.movieID.in_(movieList)) & (ActorMovie.actorName.not_in(actorNamesList)))
								.group_by(ActorMovie.nm)
								.order_by(fn.COUNT(ActorMovie.nm).desc())
								.limit(3))

	otherActorsList = []
	reasoning = {}

	for row in otherActors:
		otherActorsList.append(row.nm)
		reasoning[row.nm] = ""
		reasoning[row.nm] = row.count

	recMovies = (Movie.select().join(ActorMovie, on=(ActorMovie.movieID == Movie.movieID))
								.where((ActorMovie.nm.in_(otherActorsList)) & (Movie.movieID.not_in(movieList)))
								.order_by(Movie.rating.desc())
								.limit(5))


	return recMovies, reasoning

def recByGenres(movieList, genres):
	actors = (ActorMovie.select(ActorMovie.nm, fn.COUNT(ActorMovie.nm).alias('count'))
								.where((ActorMovie.movieID.in_(movieList)))
								.group_by(ActorMovie.nm)
								.order_by(fn.COUNT(ActorMovie.nm).desc())
								.limit(3))

	otherActorsList = []
	reasoning = {}

	for row in actors:
		otherActorsList.append(row.nm)
		reasoning[row.nm] = ""
		reasoning[row.nm] = row.count

	recMovies = (Movie.select().join(ActorMovie, on=(ActorMovie.movieID == Movie.movieID))
								.join(MovieGenre, on=(Movie.movieID == MovieGenre.movieID))
								.where((ActorMovie.nm.in_(otherActorsList)) & (MovieGenre.genre.in_(genres)))
								.order_by(Movie.rating.desc())
								.limit(5))

	return recMovies, reasoning

def recSearch(actorNamesList, movieList, genres):
	otherActors = (ActorMovie.select(ActorMovie.nm, fn.COUNT(ActorMovie.nm).alias('count'))
								.where((ActorMovie.movieID.in_(movieList)) & (ActorMovie.actorName.not_in(actorNamesList)))
								.group_by(ActorMovie.nm)
								.order_by(fn.COUNT(ActorMovie.nm).desc())
								.limit(3))

	otherActorsList = []
	reasoning = {}

	for row in otherActors:
		otherActorsList.append(row.nm)
		reasoning[row.nm] = 0
		reasoning[row.nm] = row.count

	recMovies = (Movie.select().join(ActorMovie, on=(ActorMovie.movieID == Movie.movieID))
								.join(MovieGenre, on=(Movie.movieID == MovieGenre.movieID))
								.where((ActorMovie.nm.in_(otherActorsList)) & (Movie.movieID.not_in(movieList)) & (MovieGenre.genre.in_(genres)))
								.order_by(Movie.rating.desc())
								.limit(5))

	return recMovies, reasoning






