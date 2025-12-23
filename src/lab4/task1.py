from collections import defaultdict

Movies_file = "movies.txt"
History_file = "history.txt"
class MovieRecommender:
    def __init__(self):
        self.movie_titles = {}
        self.users_history = []
        self.global_view_count = defaultdict(int)
        self.load_data()

    def load_data(self):
        with open(Movies_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split(',', 1)
                    if len(parts) == 2:
                        movie_id = int(parts[0].strip())
                        title = parts[1].strip()
                        self.movie_titles[movie_id] = title

        with open(History_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    movie_ids = set()
                    for part in line.split(','):
                        movie_id = int(part.strip())
                        movie_ids.add(movie_id)

                    if movie_ids:
                        self.users_history.append(movie_ids)
                        for movie_id in movie_ids:
                            self.global_view_count[movie_id] += 1

    def parse_user_input(self, input_str):
        if not input_str:
            return set()

        movie_ids = set()
        for part in input_str.split(','):
            movie_id = int(part.strip())
            movie_ids.add(movie_id)

        return movie_ids

    def count_common_movies(self, set1, set2):
        return len(set1.intersection(set2))

    def get_recommendation(self, current_user_movies):
        if not current_user_movies:
            raise ValueError("Список просмотренных фильмов пуст")

        # Шаг 1: Выбираем пользователей с хотя бы половиной совпадений
        similar_users = []
        threshold = len(current_user_movies) / 2.0

        for idx, user_movies in enumerate(self.users_history):
            common_count = self.count_common_movies(current_user_movies, user_movies)
            if common_count >= threshold:
                similar_users.append(user_movies)


        # Шаг 2: Собираем фильмы, которые текущий пользователь не смотрел
        candidate_movies = {}

        for user_movies in similar_users:
            for movie_id in user_movies:
                if movie_id not in current_user_movies:
                    # Используем глобальное количество просмотров
                    candidate_movies[movie_id] = self.global_view_count.get(movie_id, 0)

        if not candidate_movies:
            raise ValueError("Не найдено фильмов для рекомендации")

        # Шаг 3: Выбираем фильм с максимальным количеством просмотров
        # Сортируем по количеству просмотров (убыванию), затем по ID (для стабильности)
        sorted_candidates = sorted(
            candidate_movies.items(),
            key=lambda x: (x[1], x[0]),
            reverse=True
        )

        recommended_movie_id, max_views = sorted_candidates[0]



        return self.movie_titles[recommended_movie_id]

    def run_interactive(self):
        while True:
            try:
                print("\nВведите идентификаторы просмотренных фильмов через запятую")
                print("(или 'exit' для выхода):")

                user_input = input("> ").strip()

                if user_input.lower() in ['exit', 'quit', 'выход']:
                    print("До свидания!")
                    break

                if not user_input:
                    print("Ошибка: ввод не может быть пустым")
                    continue

                # Парсим ввод пользователя
                current_user_movies = self.parse_user_input(user_input)

                if not current_user_movies:
                    print("Ошибка: не удалось распознать ни одного идентификатора фильма")
                    continue

                # Проверяем, что все фильмы существуют в базе
                unknown_movies = [mid for mid in current_user_movies if mid not in self.movie_titles]
                if unknown_movies:
                    print(f"Предупреждение: следующие ID не найдены в базе: {unknown_movies}")

                # Получаем рекомендацию
                recommendation = self.get_recommendation(current_user_movies)
                print(f"Рекомендуемый фильм: {recommendation}")


            except ValueError as e:
                print(f"Ошибка: {e}")
            except KeyboardInterrupt:
                print("\n\nПрограмма прервана пользователем")
                break
            except Exception as e:
                print(f"Неожиданная ошибка: {e}")
                break


def main():
    """Основная функция программы"""
    try:
        # Инициализируем и запускаем рекомендатель
        recommender = MovieRecommender()
        recommender.run_interactive()

    except Exception as e:
        print(f"Критическая ошибка при запуске: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())