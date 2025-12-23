import sys
from dataclasses import dataclass
from typing import List, Dict, Optional, Iterator


class AgeGroupBoundaries:
    """Класс для хранения и валидации границ возрастных групп"""
    def __init__(self, boundaries: List[int]):
        self._validate_boundaries(boundaries)
        self._boundaries = sorted(boundaries)

    def _validate_boundaries(self, boundaries: List[int]) -> None:
        """Проверяет корректность границ возрастных групп"""
        if not boundaries:
            raise ValueError("Не указаны границы возрастных групп")

        for boundary in boundaries:
            if boundary <= 0:
                raise ValueError(f"Граница должна быть положительной: {boundary}")

        # Проверяем уникальность границ
        if len(set(boundaries)) != len(boundaries):
            raise ValueError("Границы не должны повторяться")

    @property
    def boundaries(self) -> List[int]:
        """Возвращает список границ (только для чтения)"""
        return self._boundaries.copy()

    def get_group_label(self, age: int) -> str:
        """Возвращает метку возрастной группы для заданного возраста"""
        if age > self._boundaries[-1]:
            return f"{self._boundaries[-1] + 1}+"

        lower_bound = 0
        for upper_bound in self._boundaries:
            if lower_bound <= age <= upper_bound:
                if lower_bound == 0:
                    return f"0-{upper_bound}"
                return f"{lower_bound + 1}-{upper_bound}"
            lower_bound = upper_bound

        # Должно быть недостижимо, но на всякий случай
        return f"{self._boundaries[-1] + 1}+"

    def get_all_group_labels_desc(self) -> List[str]:
        """Возвращает все возможные метки групп в порядке от старшей к младшей"""
        labels = []

        # Старшая группа
        labels.append(f"{self._boundaries[-1] + 1}+")

        # Промежуточные группы (в обратном порядке)
        for i in range(len(self._boundaries) - 1, 0, -1):
            labels.append(f"{self._boundaries[i - 1] + 1}-{self._boundaries[i]}")

        # Младшая группа
        labels.append(f"0-{self._boundaries[0]}")

        return labels


@dataclass(frozen=True, order=True)
class Respondent:
    """Класс для представления респондента"""

    name: str
    age: int

    def __post_init__(self):
        """Валидация данных респондента после инициализации"""
        if not self.name.strip():
            raise ValueError("Имя не может быть пустым")
        if self.age < 0 or self.age > 123:
            raise ValueError(f"Возраст должен быть от 0 до 123 лет: {self.age}")

    def __str__(self) -> str:
        return f"{self.name} ({self.age})"


class RespondentParser:
    """Класс для парсинга респондентов из входного потока"""

    @staticmethod
    def parse_line(line: str) -> Optional[Respondent]:
        """Парсит одну строку с информацией о респонденте"""
        line = line.strip()
        if not line or line == "END":
            return None

        parts = line.split(',')
        if len(parts) != 2:
            return None

        name, age_str = parts[0].strip(), parts[1].strip()

        try:
            age = int(age_str)
            return Respondent(name=name, age=age)
        except (ValueError, TypeError):
            return None

    @classmethod
    def parse_from_stdin(cls) -> List[Respondent]:
        """Читает и парсит респондентов из стандартного ввода"""
        respondents = []

        for line in sys.stdin:
            respondent = cls.parse_line(line)
            if respondent is None:
                if line.strip() == "END":
                    break
                continue
            respondents.append(respondent)

        return respondents


class AgeGroup:
    """Класс для представления возрастной группы с респондентами"""

    def __init__(self, label: str):
        self.label = label
        self._respondents: List[Respondent] = []

    def add_respondent(self, respondent: Respondent) -> None:
        """Добавляет респондента в группу"""
        self._respondents.append(respondent)

    def sort_respondents(self) -> None:
        """Сортирует респондентов в группе по требованиям задачи"""
        # Сначала по убыванию возраста, затем по возрастанию имени
        self._respondents.sort(key=lambda r: (-r.age, r.name))

    @property
    def respondents(self) -> List[Respondent]:
        """Возвращает список респондентов (только для чтения)"""
        return self._respondents.copy()

    @property
    def is_empty(self) -> bool:
        """Проверяет, пуста ли группа"""
        return len(self._respondents) == 0

    def __str__(self) -> str:
        """Форматирует группу для вывода"""
        if self.is_empty:
            return ""

        respondents_str = ", ".join(str(r) for r in self._respondents)
        return f"{self.label}: {respondents_str}"


class AgeGroupManager:
    """Менеджер для управления возрастными группами"""

    def __init__(self, boundaries: AgeGroupBoundaries):
        self.boundaries = boundaries
        self._groups: Dict[str, AgeGroup] = {}
        self._initialize_groups()

    def _initialize_groups(self) -> None:
        """Инициализирует все возможные возрастные группы"""
        for label in self.boundaries.get_all_group_labels_desc():
            self._groups[label] = AgeGroup(label)

    def assign_respondent(self, respondent: Respondent) -> None:
        """Назначает респондента в соответствующую возрастную группу"""
        label = self.boundaries.get_group_label(respondent.age)
        self._groups[label].add_respondent(respondent)

    def process_respondents(self, respondents: List[Respondent]) -> None:
        """Обрабатывает список респондентов, распределяя их по группам"""
        for respondent in respondents:
            self.assign_respondent(respondent)

        # Сортируем респондентов в каждой группе
        for group in self._groups.values():
            group.sort_respondents()

    def get_non_empty_groups(self) -> Iterator[AgeGroup]:
        """Возвращает итератор по непустым группам"""
        # Возвращаем группы в порядке от старшей к младшей
        for label in self.boundaries.get_all_group_labels_desc():
            group = self._groups[label]
            if not group.is_empty:
                yield group


class SurveyAnalyzer:
    """Основной класс приложения для анализа опроса"""

    def __init__(self, boundaries_args: List[str]):
        try:
            boundaries_ints = [int(arg) for arg in boundaries_args]
            self.boundaries = AgeGroupBoundaries(boundaries_ints)
            self.group_manager = AgeGroupManager(self.boundaries)
        except ValueError as e:
            raise ValueError(f"Ошибка в аргументах: {e}")

    def run(self) -> None:
        """Запускает анализ опроса"""
        # Чтение респондентов
        respondents = RespondentParser.parse_from_stdin()

        # Обработка респондентов
        self.group_manager.process_respondents(respondents)

        # Вывод результатов
        self.print_results()

    def print_results(self) -> None:
        """Выводит результаты анализа"""
        for group in self.group_manager.get_non_empty_groups():
            print(group)


def main():
    """Точка входа в приложение"""

    try:
        print("Начало работы приложения(Введите группы возрастов)")
        boundaries = [int(i) for i in input().split()]
        analyzer = SurveyAnalyzer(boundaries)
        analyzer.run()
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()


