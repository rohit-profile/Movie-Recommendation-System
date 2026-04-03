from flask import Flask, render_template, request
import pickle
import pandas as pd
import requests

app = Flask(__name__)

# Load data
movies_dict = pickle.load(open('movies_model.pkl', 'rb'))
movies_list = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity_model.pkl', 'rb'))

def fetch_poster(movie_id):
    response = requests.get(
        f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=7db733e108a1ed591f94cd66d160b97b&language=en-US'
    )
    data = response.json()
    return "https://image.tmdb.org/t/p/w500/" + data['poster_path']

def recommend(movie):
    movie_index = movies_list[movies_list['title'] == movie].index[0]
    distances = similarity[movie_index]

    movie_list = sorted(list(enumerate(distances)),
                        reverse=True,
                        key=lambda x: x[1])[1:6]

    recommend_movies = []
    recommend_posters = []

    for i in movie_list:
        movie_id = movies_list.iloc[i[0]].id
        recommend_movies.append(movies_list.iloc[i[0]].title)
        recommend_posters.append(fetch_poster(movie_id))

    return recommend_movies, recommend_posters


@app.route('/', methods=['GET', 'POST'])
def index():
    names = []
    posters = []

    if request.method == 'POST':
        selected_movie = request.form.get('movie')
        names, posters = recommend(selected_movie)

    return render_template(
        'index.html',
        movies=movies_list['title'].values,
        names=names,
        posters=posters
    )

if __name__ == '__main__':
    app.run(debug=True)