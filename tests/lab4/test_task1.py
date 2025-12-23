import unittest
from unittest.mock import mock_open, patch
import tempfile
import os
from io import StringIO
from src.lab4.task1 import MovieRecommender


class TestMovieRecommender(unittest.TestCase):

    def setUp(self):
        """Создаем временные файлы для тестирования"""
        # Создаем временные файлы
        self.movies_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        self.history_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')

        # Записываем тестовые данные
        movies_data = """1,The Matrix
2,Inception
3,Interstellar
4,The Shawshank Redemption
5,The Godfather
6,Pulp Fiction
7,Forrest Gump
8,Fight Club
9,The Dark Knight
10,Goodfellas"""

        history_data = """1,2,3
2,3,4,5
1,4,6,7
3,5,8
2,4,6,8,10
1,3,5,7,9
4,6,8,10"""

        self.movies_file.write(movies_data)
        self.history_file.write(history_data)
        self.movies_file.close()
        self.history_file.close()

        # Сохраняем оригинальные имена файлов
        self.original_movies_file = None
        self.original_history_file = None

    def tearDown(self):
        """Удаляем временные файлы"""
        os.unlink(self.movies_file.name)
        os.unlink(self.history_file.name)

    def test_init_and_load_data(self):
        """Тест инициализации и загрузки данных"""
        # Временно подменяем глобальные переменные
        import src.lab4.task1  # Замените src.lab4.task1 на имя вашего файла
        self.original_movies_file = src.lab4.task1.Movies_file
        self.original_history_file = src.lab4.task1.History_file

        src.lab4.task1.Movies_file = self.movies_file.name
        src.lab4.task1.History_file = self.history_file.name

        try:
            recommender = MovieRecommender()

            # Проверяем загрузку фильмов
            self.assertEqual(len(recommender.movie_titles), 10)
            self.assertEqual(recommender.movie_titles[1], "The Matrix")
            self.assertEqual(recommender.movie_titles[10], "Goodfellas")

            # Проверяем загрузку истории
            self.assertEqual(len(recommender.users_history), 7)
            self.assertEqual(recommender.users_history[0], {1, 2, 3})
            self.assertEqual(recommender.users_history[-1], {4, 6, 8, 10})

            # Проверяем глобальные просмотры
            self.assertGreater(recommender.global_view_count[1], 0)
            self.assertGreater(recommender.global_view_count[4], 0)

        finally:
            # Восстанавливаем оригинальные значения
            src.lab4.task1.Movies_file = self.original_movies_file
            src.lab4.task1.History_file = self.original_history_file

    def test_parse_user_input_valid(self):
        """Тест парсинга корректного ввода пользователя"""
        recommender = MovieRecommender.__new__(MovieRecommender)

        # Тест с обычным вводом
        result = recommender.parse_user_input("1,2,3")
        self.assertEqual(result, {1, 2, 3})

        # Тест с пробелами
        result = recommender.parse_user_input(" 1 , 2 , 3 ")
        self.assertEqual(result, {1, 2, 3})

        # Тест с одним числом
        result = recommender.parse_user_input("5")
        self.assertEqual(result, {5})

        # Тест с дубликатами
        result = recommender.parse_user_input("1,2,1,3,2")
        self.assertEqual(result, {1, 2, 3})

        # Тест с пустой строкой
        result = recommender.parse_user_input("")
        self.assertEqual(result, set())

        # Тест с пробелами и табуляцией
        result = recommender.parse_user_input("1,\t2,  3")
        self.assertEqual(result, {1, 2, 3})

    def test_parse_user_input_invalid(self):
        """Тест парсинга некорректного ввода"""
        recommender = MovieRecommender.__new__(MovieRecommender)

        # Тест с некорректными данными (должно вызывать ValueError)
        with self.assertRaises(ValueError):
            recommender.parse_user_input("1,a,3")

        with self.assertRaises(ValueError):
            recommender.parse_user_input("1.5,2,3")

    def test_count_common_movies(self):
        """Тест подсчета общих фильмов"""
        recommender = MovieRecommender.__new__(MovieRecommender)

        # Тест с общими элементами
        set1 = {1, 2, 3, 4}
        set2 = {3, 4, 5, 6}
        result = recommender.count_common_movies(set1, set2)
        self.assertEqual(result, 2)

        # Тест без общих элементов
        set1 = {1, 2, 3}
        set2 = {4, 5, 6}
        result = recommender.count_common_movies(set1, set2)
        self.assertEqual(result, 0)

        # Тест с пустыми множествами
        set1 = set()
        set2 = {1, 2, 3}
        result = recommender.count_common_movies(set1, set2)
        self.assertEqual(result, 0)

        # Тест с одинаковыми множествами
        set1 = {1, 2, 3}
        set2 = {1, 2, 3}
        result = recommender.count_common_movies(set1, set2)
        self.assertEqual(result, 3)

    @patch('src.lab4.task1.Movies_file', 'test_movies.txt')
    @patch('src.lab4.task1.History_file', 'test_history.txt')
    def test_get_recommendation_success(self):
        """Тест успешного получения рекомендации"""
        # Мокаем файлы
        movies_content = """1,The Matrix\n2,Inception\n3,Interstellar\n4,Shawshank"""
        history_content = """1,2,3\n2,3,4\n1,4\n3,4"""

        with patch('builtins.open', side_effect=[
            mock_open(read_data=movies_content).return_value,
            mock_open(read_data=history_content).return_value
        ]):
            recommender = MovieRecommender()

            # Тест 1: пользователь смотрел фильмы 1,2 - должен получить рекомендацию
            result = recommender.get_recommendation({1, 2})
            self.assertIn(result, ["Interstellar", "Shawshank"])

            # Тест 2: пользователь смотрел все фильмы
            with self.assertRaises(ValueError):
                recommender.get_recommendation({1, 2, 3, 4})





    @patch('src.lab4.task1.Movies_file', 'test_movies.txt')
    @patch('src.lab4.task1.History_file', 'test_history.txt')
    def test_get_recommendation_tie_breaking(self):
        """Тест разрешения ничьей при одинаковом количестве просмотров"""
        movies_content = """1,The Matrix\n2,Inception\n3,Interstellar\n4,Shawshank"""
        history_content = """1,2\n3,4\n1,3\n2,4"""

        with patch('builtins.open', side_effect=[
            mock_open(read_data=movies_content).return_value,
            mock_open(read_data=history_content).return_value
        ]):
            recommender = MovieRecommender()

            # Фильмы 2 и 3 имеют одинаковое количество просмотров в истории
            # Должен вернуться фильм с большим ID (из-за reverse сортировки)
            result = recommender.get_recommendation({1})
            # Фильм 1 не должен быть рекомендован (уже просмотрен)
            self.assertNotEqual(result, "The Matrix")

    def test_run_interactive_exit_command(self):
        """Тест интерактивного режима с командой выхода"""
        recommender = MovieRecommender.__new__(MovieRecommender)
        recommender.movie_titles = {1: "The Matrix", 2: "Inception"}
        recommender.users_history = [{1, 2}, {2}]
        recommender.global_view_count = {1: 1, 2: 2}

        # Тестируем команду выхода
        with patch('builtins.input', side_effect=['exit']):
            with patch('sys.stdout', new=StringIO()) as fake_output:
                try:
                    recommender.run_interactive()
                except StopIteration:
                    pass

                output = fake_output.getvalue()
                self.assertIn("До свидания", output)

    def test_run_interactive_invalid_input(self):
        """Тест интерактивного режима с некорректным вводом"""
        recommender = MovieRecommender.__new__(MovieRecommender)
        recommender.movie_titles = {1: "The Matrix", 2: "Inception"}
        recommender.users_history = [{1, 2}, {2}]
        recommender.global_view_count = {1: 1, 2: 2}

        # Тестируем пустой ввод
        with patch('builtins.input', side_effect=['', 'exit']):
            with patch('sys.stdout', new=StringIO()) as fake_output:
                try:
                    recommender.run_interactive()
                except StopIteration:
                    pass

                output = fake_output.getvalue()
                self.assertIn("Ошибка: ввод не может быть пустым", output)

    @patch('src.lab4.task1.Movies_file', 'test_movies.txt')
    @patch('src.lab4.task1.History_file', 'test_history.txt')
    def test_integration(self):
        """Интеграционный тест"""
        movies_content = """1,The Matrix\n2,Inception\n3,Interstellar"""
        history_content = """1,2\n2,3\n1,3"""

        with patch('builtins.open', side_effect=[
            mock_open(read_data=movies_content).return_value,
            mock_open(read_data=history_content).return_value
        ]):
            recommender = MovieRecommender()

            # Пользователь смотрел только фильм 1
            recommendation = recommender.get_recommendation({1})

            # Ожидаем, что рекомендация будет либо 2, либо 3
            self.assertIn(recommendation, ["Inception", "Interstellar"])

            # Проверяем, что не рекомендуем уже просмотренный фильм
            self.assertNotEqual(recommendation, "The Matrix")

    def test_main_function(self):
        """Тест основной функции"""
        with patch('src.lab4.task1.MovieRecommender') as MockRecommender:
            mock_instance = MockRecommender.return_value
            mock_instance.run_interactive.return_value = None

            # Импортируем main из вашего модуля
            from src.lab4.task1 import main

            result = main()
            self.assertEqual(result, 0)

            # Проверяем, что run_interactive был вызван
            mock_instance.run_interactive.assert_called_once()


class TestMovieRecommenderFileErrors(unittest.TestCase):
    """Тесты для обработки ошибок файлов"""

    def test_missing_movies_file(self):
        """Тест отсутствия файла с фильмами"""
        with patch('src.lab4.task1.Movies_file', 'nonexistent_movies.txt'):
            with patch('src.lab4.task1.History_file', 'nonexistent_history.txt'):
                with self.assertRaises(FileNotFoundError):
                    MovieRecommender()

    def test_empty_movies_file(self):
        """Тест пустого файла с фильмами"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as empty_file:
            empty_file.write("")

        try:
            with patch('src.lab4.task1.Movies_file', empty_file.name):
                with patch('src.lab4.task1.History_file', empty_file.name):
                    recommender = MovieRecommender()
                    self.assertEqual(len(recommender.movie_titles), 0)
                    self.assertEqual(len(recommender.users_history), 0)
        finally:
            os.unlink(empty_file.name)


if __name__ == '__main__':
    unittest.main()