import re
from collections import Counter
from typing import List


class Order:
    def __init__(self, raw_line: str):
        self.raw_line = raw_line.strip()
        self.errors = []
        self.valid = True
        self.parse_line()

    def parse_line(self):
        parts = self.raw_line.split(';')
        if len(parts) != 6:
            self.valid = False
            return

        self.order_number = parts[0].strip()
        self.products_raw = parts[1].strip()
        self.customer_name = parts[2].strip()
        self.delivery_address = parts[3].strip()
        self.phone_number = parts[4].strip()
        self.delivery_priority = parts[5].strip()

        self.validate_order()

    def validate_order(self):
        if not self.delivery_address:
            self.errors.append((1, "no data"))
        else:
            address_parts = [part.strip() for part in self.delivery_address.split('.')]
            if len(address_parts) < 4:
                self.errors.append((1, self.delivery_address))
            elif not all(address_parts):
                self.errors.append((1, self.delivery_address))

        if not self.phone_number:
            self.errors.append((2, "no data"))
        else:
            phone_pattern = r'^\+\d-\d{3}-\d{3}-\d{2}-\d{2}$'
            if not re.match(phone_pattern, self.phone_number):
                self.errors.append((2, self.phone_number))

    def format_products(self) -> str:
        """формат сохранения заказа 'Бананы x4, Гречка x2, Сметана'"""
        products_list = [p.strip() for p in self.products_raw.split(',')]
        product_counts = Counter(products_list)
        formatted_products = []
        for product, count in product_counts.items():
            if count > 1:
                formatted_products.append(f"{product} x{count}")
            else:
                formatted_products.append(product)

        return ', '.join(formatted_products)

    def format_address(self) -> str:
        """Формат адреса 'Регион. Город. Улица'"""
        if not self.delivery_address:
            return ""

        address_parts = [part.strip() for part in self.delivery_address.split('.')]
        if len(address_parts) >= 4:
            return f"{address_parts[1]}. {address_parts[2]}. {address_parts[3]}"
        return self.delivery_address

    def get_country(self) -> str:
        """Отделение страны от адреса"""
        if not self.delivery_address:
            return ""

        address_parts = [part.strip() for part in self.delivery_address.split('.')]
        if address_parts:
            return address_parts[0]
        return ""


def read_orders(filename: str) -> List[Order]:
    orders = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                orders.append(Order(line))
    return orders


def save_non_valid_orders(orders: List[Order], filename: str):
    with open(filename, 'w', encoding='utf-8') as f:
        for order in orders:
            if order.errors:
                for error_type, error_value in order.errors:
                    f.write(f"{order.order_number};{error_type};{error_value}\n")


def save_valid_orders(orders: List[Order], filename: str):
    valid_orders = [order for order in orders if not order.errors]
    priority_order = {"MAX": 0, "MIDDLE": 1, "LOW": 2}
    valid_orders.sort(key=lambda x: priority_order[x.delivery_priority])
    def country_sort_key(order):
        country = order.get_country()
        if country.lower() == "россия" or country.lower() == "российская федерация":
            return (0, country)
        return (1, country)

    valid_orders.sort(key=country_sort_key)

    with open(filename, 'w', encoding='utf-8') as f:
        for order in valid_orders:
            formatted_line = (
                f"{order.order_number};"
                f"{order.format_products()};"
                f"{order.customer_name};"
                f"{order.format_address()};"
                f"{order.phone_number};"
                f"{order.delivery_priority}"
            )
            f.write(formatted_line + '\n')


def main():
    orders = read_orders('orders.txt')
    save_non_valid_orders(orders, 'non_valid_orders.txt')
    save_valid_orders(orders, 'order_country.txt')


if __name__ == "__main__":
    main()