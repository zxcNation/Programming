import unittest
from unittest.mock import patch, mock_open, MagicMock
from io import StringIO
import sys
from typing import List
import tempfile
import os

# Импортируем классы для тестирования
from src.lab4.task2 import (
    AgeGroupBoundaries,
    Respondent,
    RespondentParser,
    AgeGroup,
    AgeGroupManager,
    SurveyAnalyzer,
)


class TestAgeGroupBoundaries(unittest.TestCase):
    """Тесты для класса AgeGroupBoundaries"""

    def test_init_valid_boundaries(self):
        """Тест корректной инициализации границ"""
        boundaries = AgeGroupBoundaries([18, 35, 50])
        self.assertEqual(boundaries.boundaries, [18, 35, 50])

    def test_init_sorted_boundaries(self):
        """Тест, что границы сортируются при инициализации"""
        boundaries = AgeGroupBoundaries([50, 18, 35])
        self.assertEqual(boundaries.boundaries, [18, 35, 50])

    def test_init_empty_boundaries(self):
        """Тест инициализации с пустым списком границ"""
        with self.assertRaises(ValueError) as context:
            AgeGroupBoundaries([])
        self.assertIn("Не указаны границы возрастных групп", str(context.exception))

    def test_init_negative_boundary(self):
        """Тест инициализации с отрицательной границей"""
        with self.assertRaises(ValueError) as context:
            AgeGroupBoundaries([-5, 18, 35])
        self.assertIn("Граница должна быть положительной", str(context.exception))

    def test_init_zero_boundary(self):
        """Тест инициализации с нулевой границей"""
        with self.assertRaises(ValueError) as context:
            AgeGroupBoundaries([0, 18, 35])
        self.assertIn("Граница должна быть положительной", str(context.exception))

    def test_init_duplicate_boundaries(self):
        """Тест инициализации с дублирующимися границами"""
        with self.assertRaises(ValueError) as context:
            AgeGroupBoundaries([18, 35, 18, 50])
        self.assertIn("Границы не должны повторяться", str(context.exception))

    def test_boundaries_property_readonly(self):
        """Тест, что свойство boundaries возвращает копию"""
        boundaries = AgeGroupBoundaries([18, 35, 50])
        original = boundaries.boundaries
        original.append(70)  # Попытка изменить копию
        self.assertEqual(boundaries.boundaries, [18, 35, 50])  # Оригинал не изменился

    def test_get_group_label_single_boundary(self):
        """Тест получения метки группы для одного порога"""
        boundaries = AgeGroupBoundaries([18])

        # Младше или равно границе
        self.assertEqual(boundaries.get_group_label(0), "0-18")
        self.assertEqual(boundaries.get_group_label(10), "0-18")
        self.assertEqual(boundaries.get_group_label(18), "0-18")

        # Старше границы
        self.assertEqual(boundaries.get_group_label(19), "19+")
        self.assertEqual(boundaries.get_group_label(100), "19+")

    def test_get_group_label_multiple_boundaries(self):
        """Тест получения метки группы для нескольких порогов"""
        boundaries = AgeGroupBoundaries([18, 35, 50])

        # Младшая группа
        self.assertEqual(boundaries.get_group_label(0), "0-18")
        self.assertEqual(boundaries.get_group_label(10), "0-18")
        self.assertEqual(boundaries.get_group_label(18), "0-18")

        # Средние группы
        self.assertEqual(boundaries.get_group_label(19), "19-35")
        self.assertEqual(boundaries.get_group_label(30), "19-35")
        self.assertEqual(boundaries.get_group_label(35), "19-35")

        self.assertEqual(boundaries.get_group_label(36), "36-50")
        self.assertEqual(boundaries.get_group_label(45), "36-50")
        self.assertEqual(boundaries.get_group_label(50), "36-50")

        # Старшая группа
        self.assertEqual(boundaries.get_group_label(51), "51+")
        self.assertEqual(boundaries.get_group_label(100), "51+")

    def test_get_all_group_labels_desc_single_boundary(self):
        """Тест получения всех меток групп для одного порога"""
        boundaries = AgeGroupBoundaries([18])
        labels = boundaries.get_all_group_labels_desc()
        self.assertEqual(labels, ["19+", "0-18"])

    def test_get_all_group_labels_desc_multiple_boundaries(self):
        """Тест получения всех меток групп для нескольких порогов"""
        boundaries = AgeGroupBoundaries([18, 35, 50])
        labels = boundaries.get_all_group_labels_desc()
        self.assertEqual(labels, ["51+", "36-50", "19-35", "0-18"])


class TestRespondent(unittest.TestCase):
    """Тесты для класса Respondent"""

    def test_init_valid(self):
        """Тест корректной инициализации респондента"""
        respondent = Respondent(name="John Doe", age=30)
        self.assertEqual(respondent.name, "John Doe")
        self.assertEqual(respondent.age, 30)

    def test_init_empty_name(self):
        """Тест инициализации с пустым именем"""
        with self.assertRaises(ValueError) as context:
            Respondent(name="   ", age=30)
        self.assertIn("Имя не может быть пустым", str(context.exception))

    def test_init_name_with_spaces(self):
        """Тест инициализации с именем, содержащим пробелы"""
        respondent = Respondent(name="  John Doe  ", age=30)
        self.assertEqual(respondent.name, "  John Doe  ")

    def test_init_negative_age(self):
        """Тест инициализации с отрицательным возрастом"""
        with self.assertRaises(ValueError) as context:
            Respondent(name="John", age=-5)
        self.assertIn("Возраст должен быть от 0 до 123 лет", str(context.exception))

    def test_init_age_too_high(self):
        """Тест инициализации с возрастом больше 123"""
        with self.assertRaises(ValueError) as context:
            Respondent(name="John", age=150)
        self.assertIn("Возраст должен быть от 0 до 123 лет", str(context.exception))

    def test_init_age_boundary_values(self):
        """Тест граничных значений возраста"""
        # Минимальный возраст
        respondent = Respondent(name="Baby", age=0)
        self.assertEqual(respondent.age, 0)

        # Максимальный возраст
        respondent = Respondent(name="Oldest", age=123)
        self.assertEqual(respondent.age, 123)

    def test_str_representation(self):
        """Тест строкового представления"""
        respondent = Respondent(name="John Doe", age=30)
        self.assertEqual(str(respondent), "John Doe (30)")

    def test_ordering(self):
        """Тест возможности сравнения респондентов (т.к. используется order=True)"""
        r1 = Respondent(name="Alice", age=25)
        r2 = Respondent(name="Bob", age=30)
        r3 = Respondent(name="Alice", age=30)

        # Проверяем, что можно сортировать
        respondents = [r2, r1, r3]
        sorted_respondents = sorted(respondents)
        self.assertEqual(sorted_respondents, [r1, r3, r2])


class TestRespondentParser(unittest.TestCase):
    """Тесты для класса RespondentParser"""

    def test_parse_line_valid(self):
        """Тест парсинга корректной строки"""
        respondent = RespondentParser.parse_line("John Doe,30")
        self.assertIsInstance(respondent, Respondent)
        self.assertEqual(respondent.name, "John Doe")
        self.assertEqual(respondent.age, 30)

    def test_parse_line_with_spaces(self):
        """Тест парсинга строки с пробелами"""
        respondent = RespondentParser.parse_line("  John Doe  ,  30  ")
        self.assertIsInstance(respondent, Respondent)
        self.assertEqual(respondent.name, "John Doe")
        self.assertEqual(respondent.age, 30)

    def test_parse_line_empty(self):
        """Тест парсинга пустой строки"""
        self.assertIsNone(RespondentParser.parse_line(""))
        self.assertIsNone(RespondentParser.parse_line("   "))

    def test_parse_line_end_marker(self):
        """Тест парсинга маркера конца ввода"""
        self.assertIsNone(RespondentParser.parse_line("END"))
        self.assertIsNone(RespondentParser.parse_line("  END  "))

    def test_parse_line_wrong_format(self):
        """Тест парсинга строки в неправильном формате"""
        self.assertIsNone(RespondentParser.parse_line("John Doe"))  # Нет запятой
        self.assertIsNone(RespondentParser.parse_line("John Doe,30,extra"))  # Слишком много частей

    def test_parse_line_invalid_age(self):
        """Тест парсинга строки с некорректным возрастом"""
        self.assertIsNone(RespondentParser.parse_line("John Doe,thirty"))
        self.assertIsNone(RespondentParser.parse_line("John Doe,30.5"))
        self.assertIsNone(RespondentParser.parse_line("John Doe,"))

    def test_parse_from_stdin(self):
        """Тест парсинга из стандартного ввода"""
        test_input = """Alice,25
Bob,30
Charlie,35

END
David,40"""

        with patch('sys.stdin', StringIO(test_input)):
            respondents = RespondentParser.parse_from_stdin()

            # Должны быть распарсены только строки до END
            self.assertEqual(len(respondents), 3)
            self.assertEqual(respondents[0].name, "Alice")
            self.assertEqual(respondents[0].age, 25)
            self.assertEqual(respondents[1].name, "Bob")
            self.assertEqual(respondents[1].age, 30)
            self.assertEqual(respondents[2].name, "Charlie")
            self.assertEqual(respondents[2].age, 35)

    def test_parse_from_stdin_with_errors(self):
        """Тест парсинга из стандартного ввода с ошибками"""
        test_input = """Alice,25
InvalidLine
Bob,30
Charlie,invalid
END"""

        with patch('sys.stdin', StringIO(test_input)):
            respondents = RespondentParser.parse_from_stdin()

            # Должны быть распарсены только корректные строки
            self.assertEqual(len(respondents), 2)
            self.assertEqual(respondents[0].name, "Alice")
            self.assertEqual(respondents[0].age, 25)
            self.assertEqual(respondents[1].name, "Bob")
            self.assertEqual(respondents[1].age, 30)

    def test_parse_from_stdin_no_end(self):
        """Тест парсинга без маркера END"""
        test_input = """Alice,25
Bob,30
Charlie,35"""

        with patch('sys.stdin', StringIO(test_input)):
            respondents = RespondentParser.parse_from_stdin()

            # Должны быть распарсены все строки
            self.assertEqual(len(respondents), 3)


class TestAgeGroup(unittest.TestCase):
    """Тесты для класса AgeGroup"""

    def setUp(self):
        self.group = AgeGroup("18-35")
        self.respondent1 = Respondent("Alice", 25)
        self.respondent2 = Respondent("Bob", 30)
        self.respondent3 = Respondent("Charlie", 20)

    def test_init(self):
        """Тест инициализации группы"""
        self.assertEqual(self.group.label, "18-35")
        self.assertEqual(self.group.respondents, [])
        self.assertTrue(self.group.is_empty)

    def test_add_respondent(self):
        """Тест добавления респондентов"""
        self.group.add_respondent(self.respondent1)
        self.assertEqual(len(self.group.respondents), 1)
        self.assertFalse(self.group.is_empty)

        self.group.add_respondent(self.respondent2)
        self.assertEqual(len(self.group.respondents), 2)

    def test_respondents_property_readonly(self):
        """Тест, что свойство respondents возвращает копию"""
        self.group.add_respondent(self.respondent1)
        respondents = self.group.respondents
        respondents.append(self.respondent2)  # Попытка изменить копию
        self.assertEqual(len(self.group.respondents), 1)  # Оригинал не изменился

    def test_sort_respondents(self):
        """Тест сортировки респондентов"""
        # Добавляем в разном порядке
        self.group.add_respondent(self.respondent1)  # Alice, 25
        self.group.add_respondent(self.respondent2)  # Bob, 30
        self.group.add_respondent(self.respondent3)  # Charlie, 20

        self.group.sort_respondents()

        # Должны быть отсортированы по убыванию возраста, затем по возрастанию имени
        self.assertEqual(self.group.respondents[0], self.respondent2)  # Bob, 30
        self.assertEqual(self.group.respondents[1], self.respondent1)  # Alice, 25
        self.assertEqual(self.group.respondents[2], self.respondent3)  # Charlie, 20

    def test_sort_respondents_same_age(self):
        """Тест сортировки респондентов с одинаковым возрастом"""
        respondent4 = Respondent("David", 25)

        self.group.add_respondent(self.respondent1)  # Alice, 25
        self.group.add_respondent(respondent4)  # David, 25
        self.group.add_respondent(self.respondent3)  # Charlie, 20

        self.group.sort_respondents()

        # При одинаковом возрасте сортируем по имени
        self.assertEqual(self.group.respondents[0], self.respondent1)  # Alice, 25
        self.assertEqual(self.group.respondents[1], respondent4)  # David, 25
        self.assertEqual(self.group.respondents[2], self.respondent3)  # Charlie, 20

    def test_str_empty_group(self):
        """Тест строкового представления пустой группы"""
        self.assertEqual(str(self.group), "")

    def test_str_non_empty_group(self):
        """Тест строкового представления непустой группы"""
        self.group.add_respondent(self.respondent1)
        self.group.add_respondent(self.respondent2)
        self.group.sort_respondents()

        expected = "18-35: Bob (30), Alice (25)"
        self.assertEqual(str(self.group), expected)


class TestAgeGroupManager(unittest.TestCase):
    """Тесты для класса AgeGroupManager"""

    def setUp(self):
        boundaries = AgeGroupBoundaries([18, 35])
        self.manager = AgeGroupManager(boundaries)

        # Создаем тестовых респондентов
        self.respondents = [
            Respondent("Child", 10),  # 0-18
            Respondent("Teen", 18),  # 0-18
            Respondent("Young", 25),  # 19-35
            Respondent("Adult", 35),  # 19-35
            Respondent("Senior", 40),  # 36+
        ]

    def test_initialize_groups(self):
        """Тест инициализации групп"""
        # Должны быть созданы все группы
        group_labels = list(self.manager._groups.keys())
        self.assertEqual(group_labels, ["36+", "19-35", "0-18"])

    def test_assign_respondent(self):
        """Тест распределения респондентов по группам"""
        for respondent in self.respondents:
            self.manager.assign_respondent(respondent)

        # Проверяем распределение
        self.assertEqual(len(self.manager._groups["0-18"].respondents), 2)
        self.assertEqual(len(self.manager._groups["19-35"].respondents), 2)
        self.assertEqual(len(self.manager._groups["36+"].respondents), 1)

    def test_process_respondents(self):
        """Тест обработки списка респондентов"""
        self.manager.process_respondents(self.respondents)

        # Проверяем, что респонденты распределены
        self.assertEqual(len(self.manager._groups["0-18"].respondents), 2)
        self.assertEqual(len(self.manager._groups["19-35"].respondents), 2)
        self.assertEqual(len(self.manager._groups["36+"].respondents), 1)

        # Проверяем, что респонденты отсортированы
        group_19_35 = self.manager._groups["19-35"].respondents
        self.assertEqual(group_19_35[0].name, "Adult")  # 35 лет
        self.assertEqual(group_19_35[1].name, "Young")  # 25 лет

    def test_get_non_empty_groups(self):
        """Тест получения непустых групп"""
        # Добавляем только некоторых респондентов
        self.manager.assign_respondent(self.respondents[0])  # Child -> 0-18
        self.manager.assign_respondent(self.respondents[4])  # Senior -> 36+

        for group in self.manager._groups.values():
            group.sort_respondents()

        # Получаем непустые группы
        non_empty_groups = list(self.manager.get_non_empty_groups())

        # Должны быть только 2 группы в порядке от старшей к младшей
        self.assertEqual(len(non_empty_groups), 2)
        self.assertEqual(non_empty_groups[0].label, "36+")
        self.assertEqual(non_empty_groups[1].label, "0-18")

    def test_get_non_empty_groups_all_empty(self):
        """Тест получения непустых групп, когда все группы пусты"""
        non_empty_groups = list(self.manager.get_non_empty_groups())
        self.assertEqual(len(non_empty_groups), 0)


class TestSurveyAnalyzer(unittest.TestCase):
    """Тесты для класса SurveyAnalyzer"""

    def test_init_valid(self):
        """Тест корректной инициализации анализатора"""
        analyzer = SurveyAnalyzer(["18", "35", "50"])
        self.assertIsInstance(analyzer.boundaries, AgeGroupBoundaries)
        self.assertIsInstance(analyzer.group_manager, AgeGroupManager)

    def test_init_invalid_arguments(self):
        """Тест инициализации с некорректными аргументами"""
        with self.assertRaises(ValueError) as context:
            SurveyAnalyzer(["18", "not_a_number", "50"])
        self.assertIn("Ошибка в аргументах", str(context.exception))

    def test_init_empty_arguments(self):
        """Тест инициализации с пустыми аргументами"""
        with self.assertRaises(ValueError) as context:
            SurveyAnalyzer([])
        self.assertIn("Ошибка в аргументах", str(context.exception))

    @patch.object(RespondentParser, 'parse_from_stdin')
    @patch.object(AgeGroupManager, 'process_respondents')
    def test_run(self, mock_process, mock_parse):
        """Тест запуска анализатора"""
        # Настраиваем моки
        test_respondents = [
            Respondent("Alice", 25),
            Respondent("Bob", 30),
        ]
        mock_parse.return_value = test_respondents

        # Создаем и запускаем анализатор
        analyzer = SurveyAnalyzer(["18", "35"])

        # Мокаем вывод
        with patch('sys.stdout', new=StringIO()) as fake_output:
            analyzer.print_results = MagicMock()
            analyzer.run()

            # Проверяем вызовы
            mock_parse.assert_called_once()
            mock_process.assert_called_once_with(test_respondents)
            analyzer.print_results.assert_called_once()

    def test_print_results(self):
        """Тест вывода результатов"""
        analyzer = SurveyAnalyzer(["18", "35"])

        # Добавляем тестовых респондентов
        respondents = [
            Respondent("Alice", 25),  # 19-35
            Respondent("Bob", 40),  # 36+
            Respondent("Charlie", 10),  # 0-18
        ]

        analyzer.group_manager.process_respondents(respondents)

        # Захватываем вывод
        with patch('sys.stdout', new=StringIO()) as fake_output:
            analyzer.print_results()
            output = fake_output.getvalue().strip()

            # Проверяем формат вывода
            lines = output.split('\n')
            self.assertEqual(len(lines), 3)

            # Проверяем порядок (от старшей к младшей)
            self.assertTrue(lines[0].startswith("36+:"))
            self.assertTrue(lines[1].startswith("19-35:"))
            self.assertTrue(lines[2].startswith("0-18:"))


class TestIntegration(unittest.TestCase):
    """Интеграционные тесты"""

    def test_full_integration_single_group(self):
        """Полный интеграционный тест с одной группой"""
        boundaries = AgeGroupBoundaries([30])
        manager = AgeGroupManager(boundaries)

        respondents = [
            Respondent("Alice", 25),
            Respondent("Bob", 35),
            Respondent("Charlie", 40),
            Respondent("David", 15),
        ]

        manager.process_respondents(respondents)

        # Проверяем группы
        non_empty_groups = list(manager.get_non_empty_groups())
        self.assertEqual(len(non_empty_groups), 2)

        # Старшая группа
        self.assertEqual(non_empty_groups[0].label, "31+")
        self.assertEqual(len(non_empty_groups[0].respondents), 2)

        # Младшая группа
        self.assertEqual(non_empty_groups[1].label, "0-30")
        self.assertEqual(len(non_empty_groups[1].respondents), 2)

    def test_full_integration_multiple_groups(self):
        """Полный интеграционный тест с несколькими группами"""
        boundaries = AgeGroupBoundaries([18, 30, 50])
        manager = AgeGroupManager(boundaries)

        respondents = [
            Respondent("Alice", 10),  # 0-18
            Respondent("Bob", 18),  # 0-18
            Respondent("Charlie", 25),  # 19-30
            Respondent("David", 30),  # 19-30
            Respondent("Eve", 40),  # 31-50
            Respondent("Frank", 50),  # 31-50
            Respondent("Grace", 60),  # 51+
        ]

        manager.process_respondents(respondents)

        # Проверяем все группы
        non_empty_groups = list(manager.get_non_empty_groups())
        self.assertEqual(len(non_empty_groups), 4)

        # Проверяем порядок и содержимое
        self.assertEqual(non_empty_groups[0].label, "51+")
        self.assertEqual(non_empty_groups[1].label, "31-50")
        self.assertEqual(non_empty_groups[2].label, "19-30")
        self.assertEqual(non_empty_groups[3].label, "0-18")

        # Проверяем сортировку внутри групп
        group_19_30 = non_empty_groups[2].respondents
        self.assertEqual(group_19_30[0].name, "David")  # 30 лет
        self.assertEqual(group_19_30[1].name, "Charlie")  # 25 лет


class TestEdgeCases(unittest.TestCase):
    """Тесты граничных случаев"""

    def test_age_group_boundaries_edge_cases(self):
        """Тест граничных случаев для AgeGroupBoundaries"""
        # Граница = 1
        boundaries = AgeGroupBoundaries([1])
        self.assertEqual(boundaries.get_group_label(0), "0-1")
        self.assertEqual(boundaries.get_group_label(1), "0-1")
        self.assertEqual(boundaries.get_group_label(2), "2+")

    def test_respondent_edge_cases(self):
        """Тест граничных случаев для Respondent"""
        # Граничные значения возраста
        Respondent("Baby", 0)
        Respondent("Oldest", 123)

        # Имя с необычными символами
        Respondent("John Doe-Smith", 30)
        Respondent("Алексей", 30)  # Кириллица
        Respondent("John123", 30)  # Цифры в имени

    def test_empty_groups_handling(self):
        """Тест обработки пустых групп"""
        boundaries = AgeGroupBoundaries([18, 35])
        manager = AgeGroupManager(boundaries)

        # Ни одного респондента
        manager.process_respondents([])

        non_empty_groups = list(manager.get_non_empty_groups())
        self.assertEqual(len(non_empty_groups), 0)

        # Вывод пустых групп
        for group in manager._groups.values():
            self.assertEqual(str(group), "")

    def test_single_respondent(self):
        """Тест с одним респондентом"""
        boundaries = AgeGroupBoundaries([18, 35])
        manager = AgeGroupManager(boundaries)

        respondent = Respondent("John", 25)
        manager.process_respondents([respondent])

        non_empty_groups = list(manager.get_non_empty_groups())
        self.assertEqual(len(non_empty_groups), 1)
        self.assertEqual(non_empty_groups[0].label, "19-35")
        self.assertEqual(len(non_empty_groups[0].respondents), 1)


if __name__ == '__main__':
    unittest.main()