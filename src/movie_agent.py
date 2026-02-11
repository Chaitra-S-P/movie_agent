import json
from pathlib import Path
import requests

class MovieAgent:
    def __init__(self, data_path):
        self.data_path = Path(data_path)
        self.movies = self.load_movies()

    def load_movies(self):
        if not self.data_path.exists():
            return []

        with open(self.data_path, "r") as file:
            return json.load(file)

    def save_movies(self):
        with open(self.data_path, "w") as file:
            json.dump(self.movies, file, indent=2)

    def add_movie(self, title, genre, rating, year, watched=False):
        movie = {
            "title": title,
            "genre": genre,
            "rating": rating,
            "year": year,
            "watched": watched
        }
        self.movies.append(movie)
        self.save_movies()

    def list_movies(self):
        return self.movies

    def search_movies(self, genre):
        return [
            movie for movie in self.movies
            if movie["genre"].lower() == genre.lower()
        ]

    def recommend_movies(self, min_rating=8):
        return [
            movie for movie in self.movies
            if movie["rating"] >= min_rating
        ]

    def fetch_movie_details(self, title):
        """
        Fetch movie details from external API
        and automatically save to memory
        """
        url = "https://ghibliapi.vercel.app/films"
        response = requests.get(url, timeout=5)

        if response.status_code != 200:
            return None

        movies = response.json()

        for movie in movies:
            if movie["title"].lower() == title.lower():

                movie_data = {
                    "title": movie["title"],
                    "genre": "Animation",
                    "rating": float(movie["rt_score"]) / 10,
                    "year": int(movie["release_date"]),
                    "watched": False
                }

                # ⭐ Prevent duplicates
                if not any(
                        m["title"].lower() == movie_data["title"].lower()
                        for m in self.movies
                ):
                    self.movies.append(movie_data)
                    self.save_movies()

                return movie_data

        return None


if __name__ == "__main__":
    agent = MovieAgent("data/movies.json")

    #ASK USER FOR INPUT
    movie_name = input("\n Enter the movie name to fetch details: ")

    #agent decision: fetch from api
    movie = agent.fetch_movie_details(movie_name)

    if movie:
        print("\n Movie found from API: ")
        print(movie)
    else:
        print("\n Movie not found in external source")