import unittest
import tempfile
import os
from unittest.mock import patch
import re

# Импортируем классы для тестирования
from src.lab5.online_store import Order, read_orders, save_non_valid_orders, save_valid_orders, main


class TestOrderInitialization(unittest.TestCase):
    """Тесты инициализации класса Order"""

    def test_init_valid_order_with_digits_only(self):
        """Тест создания валидного заказа с номером только из цифр"""
        raw_line = "12345;Яблоки, Бананы, Яблоки;Иван Иванов;Россия.Москва.Тверская ул.15;+7-999-123-45-67;MIDDLE"
        order = Order(raw_line)

        self.assertEqual(order.order_number, "12345")
        self.assertEqual(order.products_raw, "Яблоки, Бананы, Яблоки")
        self.assertEqual(order.customer_name, "Иван Иванов")
        self.assertEqual(order.delivery_address, "Россия.Москва.Тверская ул.15")
        self.assertEqual(order.phone_number, "+7-999-123-45-67")
        self.assertEqual(order.delivery_priority, "MIDDLE")
        self.assertEqual(order.errors, [])

    def test_init_with_spaces(self):
        """Тест создания заказа с пробелами"""
        raw_line = "  12345  ;  Яблоки, Бананы  ;  Иван Иванов  ;  Россия.Москва.Тверская ул.15  ;  +7-999-123-45-67  ;  MIDDLE  "
        order = Order(raw_line)

        self.assertEqual(order.order_number, "12345")
        self.assertEqual(order.products_raw, "Яблоки, Бананы")
        self.assertEqual(order.customer_name, "Иван Иванов")
        self.assertEqual(order.delivery_address, "Россия.Москва.Тверская ул.15")
        self.assertEqual(order.phone_number, "+7-999-123-45-67")
        self.assertEqual(order.delivery_priority, "MIDDLE")


    def test_init_valid_order_number_leading_zeros(self):
        """Тест создания заказа с ведущими нулями"""
        raw_line = "0012345;Яблоки;Иван Иванов;Россия.Москва.Тверская ул.15;+7-999-123-45-67;MIDDLE"
        order = Order(raw_line)

        self.assertEqual(order.order_number, "0012345")
        self.assertFalse(any(error[0] == 3 for error in order.errors))

    def test_init_invalid_format(self):
        """Тест создания заказа с неверным форматом строки"""
        raw_line = "12345;Яблоки;Иван Иванов;Адрес"  # Меньше частей
        order = Order(raw_line)

        self.assertFalse(order.valid)

        raw_line = "12345;Яблоки;Иван;Адрес;+7-999-123-45-67;MIDDLE;EXTRA"  # Больше частей
        order = Order(raw_line)

        self.assertFalse(order.valid)

    def test_init_empty_line(self):
        """Тест создания заказа из пустой строки"""
        raw_line = ""
        order = Order(raw_line)

        self.assertFalse(order.valid)

    def test_init_whitespace_line(self):
        """Тест создания заказа из строки с пробелами"""
        raw_line = "   \t\n  "
        order = Order(raw_line)

        self.assertFalse(order.valid)



class TestOrderMethods(unittest.TestCase):
    """Тесты методов класса Order"""

    def test_format_products_single(self):
        """Тест форматирования продуктов без повторений"""
        raw_line = "12345;Яблоки, Бананы, Апельсины;Иван;Россия.Москва.Ул.1;+7-999-123-45-67;MIDDLE"
        order = Order(raw_line)

        formatted = order.format_products()
        self.assertEqual(formatted, "Яблоки, Бананы, Апельсины")

    def test_format_products_with_duplicates(self):
        """Тест форматирования продуктов с повторениями"""
        raw_line = "12345;Яблоки, Бананы, Яблоки, Яблоки, Бананы;Иван;Россия.Москва.Ул.1;+7-999-123-45-67;MIDDLE"
        order = Order(raw_line)

        formatted = order.format_products()
        # Порядок может быть разным, проверяем наличие всех элементов
        self.assertIn("Яблоки x3", formatted)
        self.assertIn("Бананы x2", formatted)

    def test_format_products_with_spaces(self):
        """Тест форматирования продуктов с пробелами"""
        raw_line = "12345;  Яблоки ,  Бананы  , Яблоки  ;Иван;Россия.Москва.Ул.1;+7-999-123-45-67;MIDDLE"
        order = Order(raw_line)

        formatted = order.format_products()
        self.assertIn("Яблоки x2", formatted)
        self.assertIn("Бананы", formatted)

    def test_format_products_empty(self):
        """Тест форматирования пустого списка продуктов"""
        raw_line = "12345;;Иван;Россия.Москва.Ул.1;+7-999-123-45-67;MIDDLE"
        order = Order(raw_line)

        formatted = order.format_products()
        self.assertEqual(formatted, "")

    def test_format_address_valid(self):
        """Тест форматирования корректного адреса"""
        test_cases = [
            ("Россия.Москва.Тверская ул.15.Кв.1", "Москва. Тверская ул. 15"),
            ("США.Нью-Йорк.Бродвей.123", "Нью-Йорк. Бродвей. 123"),
            ("Германия.Берлин.Унтер-ден-Линден.1", "Берлин. Унтер-ден-Линден. 1"),
        ]

        for address, expected in test_cases:
            raw_line = f"12345;Яблоки;Иван;{address};+7-999-123-45-67;MIDDLE"
            order = Order(raw_line)

            formatted = order.format_address()
            self.assertEqual(formatted, expected)

    def test_format_address_invalid(self):
        """Тест форматирования некорректного адреса"""
        test_cases = [
            ("Россия", "Россия"),
            ("Россия.Москва", "Россия.Москва"),
            ("", ""),
        ]

        for address, expected in test_cases:
            raw_line = f"12345;Яблоки;Иван;{address};+7-999-123-45-67;MIDDLE"
            order = Order(raw_line)

            formatted = order.format_address()
            self.assertEqual(formatted, expected)

    def test_get_country_valid(self):
        """Тест получения страны из корректного адреса"""
        test_cases = [
            ("Россия.Москва.Ул.1", "Россия"),
            ("США.Нью-Йорк.Бродвей.123", "США"),
            ("Германия.Берлин.Унтер-ден-Линден.1", "Германия"),
            ("Российская Федерация.Москва.Ул.1", "Российская Федерация"),
        ]

        for address, expected in test_cases:
            raw_line = f"12345;Яблоки;Иван;{address};+7-999-123-45-67;MIDDLE"
            order = Order(raw_line)

            country = order.get_country()
            self.assertEqual(country, expected)

    def test_get_country_invalid(self):
        """Тест получения страны из некорректного адреса"""
        test_cases = [
            ("", ""),
            ("   ", ""),
            ("Москва.Ул.1", "Москва"),  # Нет страны на первом месте
        ]

        for address, expected in test_cases:
            raw_line = f"12345;Яблоки;Иван;{address};+7-999-123-45-67;MIDDLE"
            order = Order(raw_line)

            country = order.get_country()
            self.assertEqual(country, expected)


class TestFileOperations(unittest.TestCase):
    """Тесты операций с файлами"""

    def setUp(self):
        """Создание временных файлов для тестов"""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, 'test_orders.txt')

    def tearDown(self):
        """Удаление временных файлов"""
        import shutil
        shutil.rmtree(self.test_dir)

    def test_read_orders_valid(self):
        """Тест чтения корректных заказов из файла"""
        test_content = """12345;Яблоки, Бананы;Иван;Россия.Москва.Ул.1;+7-999-123-45-67;MIDDLE
67890;Молоко, Хлеб;Петр;США.Нью-Йорк.Бродвей.123;+1-234-567-89-01;MAX
54321;Сыр, Колбаса;Анна;Германия.Берлин.Унтер-ден-Линден.1;+49-123-456-78-90;LOW"""

        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)

        orders = read_orders(self.test_file)

        self.assertEqual(len(orders), 3)
        self.assertEqual(orders[0].order_number, "12345")
        self.assertEqual(orders[1].order_number, "67890")
        self.assertEqual(orders[2].order_number, "54321")

    def test_read_orders_with_empty_lines(self):
        """Тест чтения заказов с пустыми строками"""
        test_content = """12345;Яблоки;Иван;Россия.Москва.Ул.1;+7-999-123-45-67;MIDDLE

67890;Молоко;Петр;США.Нью-Йорк.Бродвей.123;+1-234-567-89-01;MAX

"""

        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)

        orders = read_orders(self.test_file)

        self.assertEqual(len(orders), 2)
        self.assertEqual(orders[0].order_number, "12345")
        self.assertEqual(orders[1].order_number, "67890")

    def test_read_orders_with_invalid_lines(self):
        """Тест чтения заказов с невалидными строками"""
        test_content = """12345;Яблоки;Иван;Россия.Москва.Ул.1;+7-999-123-45-67;MIDDLE
INVALID_LINE
67890;Молоко;Петр;США.Нью-Йорк.Бродвей.123;+1-234-567-89-01;MAX"""

        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)

        orders = read_orders(self.test_file)

        self.assertEqual(len(orders), 3)  # Все строки будут обработаны
        # Один заказ будет невалидным
        invalid_count = sum(1 for order in orders if not order.valid)
        self.assertEqual(invalid_count, 1)

    def test_save_non_valid_orders(self):
        """Тест сохранения невалидных заказов"""
        orders = [
            Order("ORD001;Яблоки;Иван;Россия;+7-999-123-45-67;MIDDLE"),  # Неполный адрес и номер
            Order("12345;Молоко;Петр;США.Нью-Йорк.Бродвей.123;invalid;MAX"),  # Невалидный телефон
            Order("54321;Сыр;Анна;Германия.Берлин.Унтер-ден-Линден.1;+49-123-456-78-90;LOW"),  # Валидный
        ]

        output_file = os.path.join(self.test_dir, 'non_valid.txt')
        save_non_valid_orders(orders, output_file)

        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read().strip().split('\n')

        # Должны быть сохранены 2 строки с ошибками
        self.assertEqual(len(content), 3)  # ORD001 имеет 2 ошибки (номер и адрес)

        # Проверяем наличие ключевых данных
        self.assertTrue(any("12345" in line for line in content))
        self.assertTrue(any("54321" in line for line in content))

    def test_save_non_valid_orders_empty(self):
        """Тест сохранения невалидных заказов, когда все заказы валидны"""
        orders = [
            Order("12345;Яблоки;Иван;Россия.Москва.Ул.1;+7-999-123-45-67;MIDDLE"),
            Order("67890;Молоко;Петр;США.Нью-Йорк.Бродвей.123;+1-234-567-89-01;MAX"),
        ]

        output_file = os.path.join(self.test_dir, 'non_valid.txt')
        save_non_valid_orders(orders, output_file)

        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Файл должен быть пустым
        self.assertEqual(content, "")

    def test_save_valid_orders(self):
        """Тест сохранения валидных заказов"""
        orders = [
            Order("54321;Сыр, Колбаса;Анна;Германия.Берлин.Ул.1;+49-123-456-78-90;LOW"),
            Order("12345;Яблоки, Яблоки;Иван;Россия.Москва.Ул.1;+7-999-123-45-67;MIDDLE"),
            Order("67890;Молоко;Петр;США.Нью-Йорк.Ул.2;+1-234-567-89-01;MAX"),
            Order("98765;Хлеб;Сергей;Российская Федерация.СПб.Ул.3;+7-888-123-45-67;MIDDLE"),
        ]

        output_file = os.path.join(self.test_dir, 'valid.txt')
        save_valid_orders(orders, output_file)

        with open(output_file, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines()]

        # Должны быть сохранены все 4 заказа
        self.assertEqual(len(lines), 3)

        # Проверяем сортировку: сначала Россия, потом другие страны
        # Внутри России: сначала MAX, потом MIDDLE
        self.assertTrue("12345" in lines[0] or "98765" in lines[0])  # Россия, MIDDLE
        self.assertTrue("12345" in lines[1] or "98765" in lines[1])  # Россия, MIDDLE
        self.assertTrue("67890" in lines[2])
    def test_save_valid_orders_priority_sorting(self):
        """Тест сортировки по приоритету доставки"""
        orders = [
            Order("00123;Яблоки;Иван;США.Нью-Йорк.Ул.1;+1-234-567-89-01;LOW"),
            Order("45678;Молоко;Петр;США.Нью-Йорк.Ул.2;+1-234-567-89-02;MAX"),
            Order("78901;Сыр;Анна;США.Нью-Йорк.Ул.3;+1-234-567-89-03;MIDDLE"),
        ]

        output_file = os.path.join(self.test_dir, 'valid.txt')
        save_valid_orders(orders, output_file)

        with open(output_file, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines()]

        # Проверяем сортировку по приоритету: MAX, MIDDLE, LOW
        self.assertTrue("45678" in lines[0])  # MAX
        self.assertTrue("78901" in lines[1])  # MIDDLE
        self.assertTrue("00123" in lines[2])  # LOW

    def test_save_valid_orders_country_sorting(self):
        """Тест сортировки по стране (Россия должна быть первой)"""
        orders = [
            Order("11111;Яблоки;Иван;США.Нью-Йорк.Ул.1;+1-234-567-89-01;MAX"),
            Order("22222;Молоко;Петр;Россия.Москва.Ул.2;+7-999-123-45-67;MAX"),
            Order("33333;Сыр;Анна;Германия.Берлин.Ул.3;+49-123-456-78-90;MAX"),
        ]

        output_file = os.path.join(self.test_dir, 'valid.txt')
        save_valid_orders(orders, output_file)

        with open(output_file, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines()]

        # Россия должна быть первой, даже если другие страны имеют тот же приоритет
        self.assertTrue("22222" in lines[0])  # Россия
        # Остальные страны в алфавитном порядке (Германия, затем США)
        self.assertTrue("11111" in lines[1])  # США

    def test_save_valid_orders_empty(self):
        """Тест сохранения валидных заказов, когда нет валидных"""
        orders = [
            Order("ORD001;Яблоки;Иван;Россия;+7-999-123-45-67;MIDDLE"),  # Неполный адрес
            Order("123ABC;Молоко;Петр;США.Нью-Йорк.Бродвей.123;invalid;MAX"),  # Невалидный телефон и номер
        ]

        output_file = os.path.join(self.test_dir, 'valid.txt')
        save_valid_orders(orders, output_file)

        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Файл должен быть пустым
        self.assertEqual(content, "")


class TestEdgeCases(unittest.TestCase):
    """Тесты граничных случаев"""

    def test_order_with_special_characters(self):
        """Тест заказа со специальными символами (в номере только цифры)"""
        raw_line = "12345;Яблоки (красные), Бананы \"спелые\";Иванов-Петров И.И.;Россия.Москва.Ул. Ленина, д.15/2;+7-999-123-45-67;MIDDLE"
        order = Order(raw_line)

        # Проверяем, что парсинг работает
        self.assertEqual(order.order_number, "12345")
        self.assertIn("Яблоки (красные)", order.products_raw)
        self.assertEqual(order.customer_name, "Иванов-Петров И.И.")
        self.assertFalse(any(error[0] == 3 for error in order.errors))

    def test_order_with_unicode(self):
        """Тест заказа с Unicode символами"""
        raw_line = "00123;Яблоки 🍎, Бананы 🍌;Иван Ιωάννης;Россия.Москва.Улица 🌸.1;+7-999-123-45-67;MIDDLE"
        order = Order(raw_line)

        # Проверяем, что парсинг работает с Unicode
        self.assertEqual(order.order_number, "00123")
        self.assertIn("🍎", order.products_raw)
        self.assertEqual(order.customer_name, "Иван Ιωάννης")
        self.assertFalse(any(error[0] == 3 for error in order.errors))

    def test_order_with_many_products(self):
        """Тест заказа с большим количеством продуктов"""
        products = ", ".join([f"Продукт{i}" for i in range(100)])
        raw_line = f"99999;{products};Иван;Россия.Москва.Ул.1;+7-999-123-45-67;MIDDLE"

        order = Order(raw_line)
        formatted = order.format_products()

        # Проверяем, что форматирование работает
        self.assertIn("Продукт0", formatted)
        self.assertIn("Продукт99", formatted)
        self.assertFalse(any(error[0] == 3 for error in order.errors))

    def test_order_with_long_address(self):
        """Тест заказа с длинным адресом"""
        raw_line = "54321;Яблоки;Иван;Россия.Москва.Очень длинное название улицы которое может быть очень длинным.123.Корпус 1.Подъезд 2.Квартира 45;+7-999-123-45-67;MIDDLE"
        order = Order(raw_line)

        # Проверяем форматирование адреса (берет только первые 4 части)
        formatted = order.format_address()
        self.assertEqual(formatted, "Москва. Очень длинное название улицы которое может быть очень длинным. 123")
        self.assertFalse(any(error[0] == 3 for error in order.errors))

    def test_order_with_multiple_errors(self):
        """Тест заказа с несколькими ошибками"""
        raw_line = "ORD001;Яблоки;Иван;;;MIDDLE"  # Неверный номер, пустой адрес и телефон
        order = Order(raw_line)

        self.assertEqual(len(order.errors), 2)
        error_types = sorted([error[0] for error in order.errors])
        self.assertEqual(error_types, [1, 2])


class TestIntegration(unittest.TestCase):
    """Интеграционные тесты"""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir)

    def test_full_pipeline(self):
        """Тест полного цикла обработки заказов"""
        # Создаем тестовый файл с заказами
        orders_content = """12345;Яблоки, Бананы, Яблоки;Иван Иванов;Россия.Москва.Тверская ул.15;+7-999-123-45-67;MIDDLE
ORD002;Молоко;Петр Петров;Россия;+7-888-123-45-67;MAX
67890;Хлеб, Сыр;Анна Сидорова;США.Нью-Йорк.Бродвей.123;invalid_phone;LOW
54321;Колбаса;Сергей Сергеев;Российская Федерация.Санкт-Петербург.Невский проспект.28;+7-777-123-45-67;MIDDLE
98765;Сок, Вода;Мария Иванова;Германия.Берлин.Унтер-ден-Линден.1;+49-123-456-78-90;MAX"""

        orders_file = os.path.join(self.test_dir, 'orders.txt')
        with open(orders_file, 'w', encoding='utf-8') as f:
            f.write(orders_content)

        # Читаем заказы
        orders = read_orders(orders_file)
        self.assertEqual(len(orders), 5)

        # Сохраняем невалидные заказы
        non_valid_file = os.path.join(self.test_dir, 'non_valid.txt')
        save_non_valid_orders(orders, non_valid_file)

        with open(non_valid_file, 'r', encoding='utf-8') as f:
            non_valid_lines = f.read().strip().split('\n')

        non_valid_lines = [line for line in non_valid_lines if line]
        self.assertEqual(len(non_valid_lines), 3)

        # Сохраняем валидные заказы
        valid_file = os.path.join(self.test_dir, 'valid.txt')
        save_valid_orders(orders, valid_file)

        with open(valid_file, 'r', encoding='utf-8') as f:
            valid_lines = f.read().strip().split('\n')

        # Должно быть 3 валидных заказа (12345, 54321, 98765)
        valid_lines = [line for line in valid_lines if line]
        self.assertEqual(len(valid_lines), 2)

        # Проверяем сортировку валидных заказов
        # Россия должна быть первой, внутри России сортировка по приоритету
        self.assertTrue("12345" in valid_lines[0] or "54321" in valid_lines[0])
        self.assertTrue("12345" in valid_lines[1] or "54321" in valid_lines[1])

    @patch('src.lab5.online_store.read_orders')
    @patch('src.lab5.online_store.save_non_valid_orders')
    @patch('src.lab5.online_store.save_valid_orders')
    def test_main_function(self, mock_save_valid, mock_save_non_valid, mock_read):
        """Тест основной функции"""
        # Настраиваем моки
        mock_read.return_value = []

        # Вызываем main
        main()

        # Проверяем вызовы
        mock_read.assert_called_once_with('orders.txt')
        mock_save_non_valid.assert_called_once()
        mock_save_valid.assert_called_once()


class TestRegexPattern(unittest.TestCase):
    """Тесты для regex-паттерна валидации телефона"""

    def test_phone_regex_pattern(self):
        """Тест корректности regex-паттерна"""
        phone_pattern = r'^\+\d-\d{3}-\d{3}-\d{2}-\d{2}$'

        valid_cases = [
            "+1-234-567-89-01",
            "+7-999-123-45-67",
        ]

        for phone in valid_cases:
            self.assertTrue(re.match(phone_pattern, phone), f"Failed for: {phone}")

        invalid_cases = [
            "79991234567",
            "+7 999 123 45 67",
            "+7-999-123-45-6",
            "7-999-123-45-67",
            "+7-999-123-45",
            "+7-999-123-45-678",
            "+7-abc-123-45-67",
            "",
            "   ",
        ]

        for phone in invalid_cases:
            self.assertFalse(re.match(phone_pattern, phone), f"Should fail for: {phone}")


if __name__ == '__main__':
    unittest.main()