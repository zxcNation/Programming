import re

#Функция, определяющая приоритет операций
#(2-умножение и деление,1-сложение и вычитание, 0-скобки и другие символы)

def priority(op):
    if op == "+" or op == "-":
        return 1
    if op == "*" or op == "/":
        return 2
    return 0

def operation(operators, values):
    try:
        op = operators.pop()
        second = values.pop()
        first = values.pop()
    except:
        raise ValueError("Некорректное выражение")
    if op == "+":
        values.append(first + second)
    elif op == "-":
        values.append(first - second)
    elif op == "*":
        values.append(first * second)
    elif op == "/":
        if second == 0:
            raise ZeroDivisionError("Деление на ноль!!")
        values.append(first / second)

def calculate(expression):
    values = []
    operators = []
    expression = expression.replace(" ","")

    for elem in expression:
        if elem not in "1234567890+-*/().":
            raise ValueError(f"Недопустимый символ: {elem}")

    tokens = re.findall(r"(\d+(?:\.\d*)?|\.\d+|[+\-*/()]|[()])", expression)

    if not tokens:
        raise ValueError("Пустое или нераспознанное выражение")

    for token in tokens:
        if re.match(r"^\d+(\.\d*)?|\.\d+$", token):
            values.append(float(token))
        elif token == "(":
            operators.append(token)
        elif token == ")":
            while operators and operators[-1] != "(":
                operation(operators, values)
            try:
                operators.pop()
            except:
                raise ValueError("Неккоректное выражение")
        elif token in "+-*/":
            while operators and priority(operators[-1]) >= priority(token):
                operation(operators, values)
            operators.append(token)
        else:
            raise ValueError(f"Недопустимый символ: {token}")

    while operators:
        operation(operators, values)

    if len(values) != 1:
        raise ValueError("Некорректное выражение")

    return values[0]

if __name__ == '__main__':
    print("Введите выражение(код для отмены-'STOP'):")
    expression = input()
    while expression.upper() != "STOP":
        try:
            result = calculate(expression)
            print(f"{expression} = {result}")
            expression = input()
        except (ValueError, ZeroDivisionError) as e:
            print(f"Ошибка в выражении '{expression}': {e}")
            expression = input()

    print("Конец работы калькулятора")
