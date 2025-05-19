from flask import Flask, render_template, request, redirect, session, url_for, abort
import psycopg2

from dir.auth import login_as_guest, login_as_employee, login_as_admin

app = Flask(__name__)
app.secret_key = 'super-secret-key'

EDITABLE_TABLES = ["TouristCategories", "Locations", "Routes", "Competitions"]


conn_params = {
    "dbname": "tourists_base",
    "user": "postgres",
    "password": "100321",
    "host": "localhost",
    "port": 5432
}

TABLE_QUERIES = {
    "Туристы": """
        SELECT 
            t.id,
            t.name_,
            t.surname,
            t.patronymic,
            t.gender,
            t.age,
            t.date_of_birth,
            c.category AS category_name,
            t.skills
        FROM Tourists t
        LEFT JOIN TouristCategories c ON t.category_id = c.id
    """,
    "Разряды": """
        SELECT id, category, description
        FROM TouristCategories
    """,
    "Руководители": """
        SELECT id, name_, surname, patronymic, salary, age, date_of_birth, year_of_entry_into_employment
        FROM Leaders
    """,
    "Тренеры": """
        SELECT 
            tr.id,
            t.name_ AS tourist_name,
            t.surname AS tourist_surname,
            t.patronymic AS tourist_patronymic,
            c.category AS category,
            tr.salary,
            tr.specialization,
            tr.year_of_entry_into_employment
        FROM Trainers tr
        JOIN Tourists t ON tr.tourist_id = t.id
        LEFT JOIN TouristCategories c ON t.category_id = c.id
    """,
    "Секции": """
    SELECT 
    s.id,
    s.name_,
    CONCAT(l.surname, ' ', l.name_, ' ', l.patronymic) AS leader_full_name
    FROM Sections s
    LEFT JOIN Leaders l ON s.leader_id = l.id;
    """,
    "Группы": """
    SELECT 
    g.id,
    g.name_,
    s.name_ AS section_name,
    CONCAT(tur.surname, ' ', tur.name_, ' ', tur.patronymic) AS trainer_full_name
    FROM Groups_ g
    LEFT JOIN Sections s ON g.section_id = s.id
    LEFT JOIN Trainers tr ON g.trainer_id = tr.id
    LEFT JOIN Tourists tur ON tr.tourist_id = tur.id;
""",
    "Тренировки": """SELECT 
    trn.id,
    g.name_ AS group_name,
    trn.day_of_the_week,
    trn.start_time,
    trn.end_time,
    trn.location_,
    CONCAT(tur.surname, ' ', tur.name_, ' ', tur.patronymic) AS trainer_full_name
FROM Trainings trn
LEFT JOIN Groups_ g ON trn.group_id = g.id
LEFT JOIN Trainers tr ON trn.trainer_id = tr.id
LEFT JOIN Tourists tur ON tr.tourist_id = tur.id;
""",
    "Посещаемость": """SELECT 
    a.id,
    CONCAT(t.surname, ' ', t.name_, ' ', t.patronymic) AS tourist_full_name,
    a.date_,
    trn.day_of_the_week,
    trn.start_time,
    trn.end_time,
    a.is_present
FROM Attendance a
JOIN Tourists t ON a.tourist_id = t.id
JOIN Trainings trn ON a.training_id = trn.id;
""",
    "Локации": """SELECT 
    id, name_, difficulty, latitude, longitude, description
FROM Locations;
""",
    "Маршруты": """SELECT 
    id, name_, type_, difficulty_category, total_length, estimated_days, description
FROM Routes;
""",
    "Места": """SELECT 
    rp.id,
    r.name_ AS route_name,
    l.name_ AS location_name,
    rp.point_order,
    rp.description,
    rp.distance_from_previous
FROM RoutePoints rp
JOIN Routes r ON rp.route_id = r.id
JOIN Locations l ON rp.location_id = l.id
ORDER BY r.id, rp.point_order;
""",
    "Походы": """SELECT 
    tr.id,
    r.name_ AS route_name,
    tr.start_date,
    tr.end_date,
    CONCAT(t.surname, ' ', t.name_, ' ', t.patronymic) AS instructor_name,
    tr.status,
    tr.notes
FROM Trips tr
LEFT JOIN Routes r ON tr.route_id = r.id
LEFT JOIN Tourists t ON tr.instructor_id = t.id;
""",
    "Запланированные походы": """SELECT 
    pt.id,
    tr.id AS trip_id,
    pt.plan,
    pt.diary
FROM PlannedTrips pt
JOIN Trips tr ON pt.trip_id = tr.id;
""",
    "Участники походов": """SELECT 
    tp.id,
    tr.id AS trip_id,
    CONCAT(t.surname, ' ', t.name_, ' ', t.patronymic) AS tourist_name,
    tp.group_mark
FROM TripParticipants tp
JOIN Trips tr ON tp.trip_id = tr.id
JOIN Tourists t ON tp.tourist_id = t.id;
""",
    "Соревнования": """SELECT 
    id, name_, date, location_
FROM Competitions;
""",
    "Участники соревнований": """SELECT 
    cp.id,
    c.name_ AS competition_name,
    CONCAT(t.surname, ' ', t.name_, ' ', t.patronymic) AS tourist_name,
    cp.result_
FROM CompetitionParticipants cp
JOIN Competitions c ON cp.competition_id = c.id
JOIN Tourists t ON cp.tourist_id = t.id;
"""
}


TABLE_NAME_MAPPING = {
    "Туристы": "Tourists",
    "Разряды": "TouristCategories",
    "Руководители": "Leaders",
    "Тренеры": "Trainers",
    "Секции": "Sections",
    "Группы": "Groups_",
    "Тренировки": "Trainings",
    "Посещаемость": "Attendance",
    "Локации": "Locations",
    "Маршруты": "Routes",
    "Места": "RoutePoints",
    "Походы": "Trips",
    "Запланированные походы": "PlannedTrips",
    "Участники походов": "TripParticipants",
    "Участники соревнований": "CompetitionParticipants",
    "Соревнования": "Competitions"
}


REVERSE_TABLE_MAPPING = {v: k for k, v in TABLE_NAME_MAPPING.items()}

TABLES_META = {
    "Туристы": {
        "fields": [
            {"name": "name_", "type": "text", "label": "Имя"},
            {"name": "surname", "type": "text", "label": "Фамилия"},
            {"name": "patronymic", "type": "text", "label": "Отчество"},
            {"name": "gender", "type": "select", "label": "Пол", "options": ["мужской", "женский"]},
            {"name": "age", "type": "number", "label": "Возраст"},
            {"name": "date_of_birth", "type": "date", "label": "Дата рождения"},
            {"name": "category_id", "type": "select", "label": "Категория",
             "options_query": "SELECT id, category FROM TouristCategories"},
            {"name": "skills", "type": "text", "label": "Навыки"}
        ],
        "primary_key": "id",
        "table_name": "Tourists"
    },
    "Разряды": {
        "fields": [
            {"name": "category", "type": "text", "label": "Категория"},
            {"name": "description", "type": "text", "label": "Описание"}
        ],
        "primary_key": "id",
        "table_name": "TouristCategories"
    },
    "Руководители": {
        "fields": [
            {"name": "name_", "type": "text", "label": "Имя"},
            {"name": "surname", "type": "text", "label": "Фамилия"},
            {"name": "patronymic", "type": "text", "label": "Отчество"},
            {"name": "salary", "type": "number", "label": "Зарплата"},
            {"name": "age", "type": "number", "label": "Возраст"},
            {"name": "date_of_birth", "type": "date", "label": "Дата рождения"},
            {"name": "year_of_entry_into_employment", "type": "number", "label": "Год приёма на работу"}
        ],
        "primary_key": "id",
        "table_name": "Leaders"
    },
    "Тренеры": {
        "fields": [
            {"name": "tourist_id", "type": "select", "label": "Турист",
             "options_query": "SELECT id, surname || ' ' || name_ || ' ' || patronymic FROM Tourists"},
            {"name": "salary", "type": "number", "label": "Зарплата"},
            {"name": "specialization", "type": "text", "label": "Специализация"},
            {"name": "year_of_entry_into_employment", "type": "number", "label": "Год приёма на работу"}
        ],
        "primary_key": "id",
        "table_name": "Trainers"
    },
    "Секции": {
        "fields": [
            {"name": "name_", "type": "text", "label": "Название"},
            {"name": "leader_id", "type": "select", "label": "Руководитель",
             "options_query": "SELECT id, surname || ' ' || name_ || ' ' || patronymic FROM Leaders"}
        ],
        "primary_key": "id",
        "table_name": "Sections"
    },
    "Группы": {
        "fields": [
            {"name": "name_", "type": "text", "label": "Название"},
            {"name": "section_id", "type": "select", "label": "Секция",
             "options_query": "SELECT id, name_ FROM Sections"},
            {"name": "trainer_id", "type": "select", "label": "Тренер",
             "options_query": "SELECT t.id, tr.surname || ' ' || tr.name_ FROM Trainers t JOIN Tourists tr ON t.tourist_id = tr.id"}
        ],
        "primary_key": "id",
        "table_name": "Groups_"
    },
    "Тренировки": {
        "fields": [
            {"name": "group_id", "type": "select", "label": "Группа",
             "options_query": "SELECT id, name_ FROM Groups_"},
            {"name": "day_of_the_week", "type": "select", "label": "День недели",
             "options": ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]},
            {"name": "start_time", "type": "time", "label": "Время начала"},
            {"name": "end_time", "type": "time", "label": "Время окончания"},
            {"name": "location_", "type": "text", "label": "Локация"},
            {"name": "trainer_id", "type": "select", "label": "Тренер",
             "options_query": "SELECT t.id, tr.surname || ' ' || tr.name_ FROM Trainers t JOIN Tourists tr ON t.tourist_id = tr.id"}
        ],
        "primary_key": "id",
        "table_name": "Trainings"
    },
    "Посещаемость": {
        "fields": [
            {"name": "tourist_id", "type": "select", "label": "Турист",
             "options_query": "SELECT id, surname || ' ' || name_ || ' ' || patronymic FROM Tourists"},
            {"name": "training_id", "type": "select", "label": "Тренировка",
             "options_query": "SELECT id, day_of_the_week || ' ' || start_time || '-' || end_time FROM Trainings"},
            {"name": "date_", "type": "date", "label": "Дата"},
            {"name": "is_present", "type": "select", "label": "Присутствие", "options": ["True", "False"]}
        ],
        "primary_key": "id",
        "table_name": "Attendance"
    },
    "Локации": {
        "fields": [
            {"name": "name_", "type": "text", "label": "Название"},
            {"name": "difficulty", "type": "select", "label": "Сложность", "options": ["легкая", "средняя", "сложная"]},
            {"name": "latitude", "type": "number", "label": "Широта"},
            {"name": "longitude", "type": "number", "label": "Долгота"},
            {"name": "description", "type": "text", "label": "Описание"}
        ],
        "primary_key": "id",
        "table_name": "Locations"
    },
    "Маршруты": {
        "fields": [
            {"name": "name_", "type": "text", "label": "Название"},
            {"name": "type_", "type": "select", "label": "Тип маршрута",
             "options": ["пеший", "велосипедный", "водный"]},
            {"name": "difficulty_category", "type": "select", "label": "Категория сложности",
             "options": ["низкая", "средняя", "высокая"]},
            {"name": "total_length", "type": "number", "label": "Общая длина (км)"},
            {"name": "estimated_days", "type": "number", "label": "Оценочное время (дни)"},
            {"name": "description", "type": "text", "label": "Описание"}
        ],
        "primary_key": "id",
        "table_name": "Routes"
    },
    "Места": {
        "fields": [
            {"name": "route_id", "type": "select", "label": "Маршрут", "options_query": "SELECT id, name_ FROM Routes"},
            {"name": "location_id", "type": "select", "label": "Локация",
             "options_query": "SELECT id, name_ FROM Locations"},
            {"name": "point_order", "type": "number", "label": "Порядок точки"},
            {"name": "description", "type": "text", "label": "Описание"},
            {"name": "distance_from_previous", "type": "number", "label": "Расстояние от предыдущей (км)"}
        ],
        "primary_key": "id",
        "table_name": "RoutePoints"
    },
    "Походы": {
        "fields": [
            {"name": "route_id", "type": "select", "label": "Маршрут", "options_query": "SELECT id, name_ FROM Routes"},
            {"name": "start_date", "type": "date", "label": "Дата начала"},
            {"name": "end_date", "type": "date", "label": "Дата окончания"},
            {"name": "instructor_id", "type": "select", "label": "Инструктор",
             "options_query": "SELECT id, surname || ' ' || name_ || ' ' || patronymic FROM Tourists"},
            {"name": "status", "type": "select", "label": "Статус",
             "options": ["планируется", "в процессе", "завершён"]},
            {"name": "notes", "type": "text", "label": "Примечания"}
        ],
        "primary_key": "id",
        "table_name": "Trips"
    },
    "Запланированные походы": {
        "fields": [
            {"name": "trip_id", "type": "select", "label": "Поход",
             "options_query": "SELECT t.id, r.name_ || ' (' || t.start_date || ')' FROM Trips t JOIN Routes r ON t.route_id = r.id"},
            {"name": "plan", "type": "text", "label": "План"},
            {"name": "diary", "type": "text", "label": "Дневник"}
        ],
        "primary_key": "id",
        "table_name": "PlannedTrips"
    },
    "Участники походов": {
        "fields": [
            {"name": "trip_id", "type": "select", "label": "Поход",
             "options_query": "SELECT id, name_ FROM Trips"},
            {"name": "tourist_id", "type": "select", "label": "Турист",
             "options_query": "SELECT id, surname || ' ' || name_ FROM Tourists"},
            {"name": "group_mark", "type": "number", "label": "Номер группы"},

        ],
        "primary_key": "id",
        "table_name": "TripParticipants"
    },
    "Соревнования": {
        "fields": [
            {"name": "name_", "type": "text", "label": "Название"},
            {"name": "date", "type": "date", "label": "Дата"},
            {"name": "location_", "type": "text", "label": "Место проведения"}
        ],
        "primary_key": "id",
        "table_name": "Competitions"
    },
    "Участники соревнований": {
        "fields": [
            {"name": "competition_id", "type": "select", "label": "Соревнование",
             "options_query": "SELECT id, name_ FROM Competitions"},
            {"name": "tourist_id", "type": "select", "label": "Турист",
             "options_query": "SELECT id, surname || ' ' || name_ || ' ' || patronymic FROM Tourists"},
            {"name": "result", "type": "text", "label": "Результат"}
        ],
        "primary_key": "id",
        "table_name": "CompetitionParticipants"
    }
}

FILTER_CONFIG = {
    "Туристы": {
        "base_query": """
            SELECT t.id, t.name_, t.surname, t.patronymic, t.gender, 
                   t.age, t.date_of_birth, tc.category as category_name, t.skills,
                   s.name_ as section_name, g.name_ as group_name
            FROM Tourists t
            LEFT JOIN TouristCategories tc ON t.category_id = tc.id
            LEFT JOIN GroupParticipants gp ON t.id = gp.tourist_id
            LEFT JOIN Groups_ g ON gp.group_id = g.id
            LEFT JOIN Sections s ON g.section_id = s.id
        """,
        "filters": [
            {"name": "surname", "label": "Фамилия", "type": "text"},
            {"name": "gender", "label": "Пол", "type": "select", "options": ["мужской", "женский"]},
            {"name": "age", "label": "Возраст", "type": "number"},
            {"name": "date_of_birth", "label": "Год рождения", "type": "text", "placeholder": "ГГГГ"},
            {"name": "category_name", "label": "Категория", "type": "text"},
            {"name": "section_name", "label": "Секция", "type": "text"},
            {"name": "group_name", "label": "Группа", "type": "text"}
        ]
    },
    "Тренеры": {
        "base_query": """
            SELECT tr.id, t.name_, t.surname, t.patronymic, t.gender, t.age,
                   tr.salary, tr.specialization, tr.year_of_entry_into_employment,
                   s.name_ as section_name
            FROM Trainers tr
            JOIN Tourists t ON tr.tourist_id = t.id
            LEFT JOIN Groups_ g ON tr.id = g.trainer_id
            LEFT JOIN Sections s ON g.section_id = s.id
        """,
        "filters": [
            {"name": "surname", "label": "Фамилия", "type": "text"},
            {"name": "gender", "label": "Пол", "type": "select", "options": ["мужской", "женский"]},
            {"name": "age", "label": "Возраст", "type": "number"},
            {"name": "salary", "label": "Зарплата", "type": "number"},
            {"name": "specialization", "label": "Специализация", "type": "text"},
            {"name": "section_name", "label": "Секция", "type": "text"}
        ]
    },
    "Соревнования": {
        "base_query": """
            SELECT c.id, c.name_, c.date, c.location_,
                   COUNT(DISTINCT cp.tourist_id) as participants_count,
                   GROUP_CONCAT(DISTINCT s.name_) as sections
            FROM Competitions c
            LEFT JOIN CompetitionParticipants cp ON c.id = cp.competition_id
            LEFT JOIN Tourists t ON cp.tourist_id = t.id
            LEFT JOIN GroupParticipants gp ON t.id = gp.tourist_id
            LEFT JOIN Groups_ g ON gp.group_id = g.id
            LEFT JOIN Sections s ON g.section_id = s.id
            GROUP BY c.id
        """,
        "filters": [
            {"name": "name_", "label": "Название", "type": "text"},
            {"name": "date", "label": "Дата", "type": "date"},
            {"name": "location_", "label": "Место проведения", "type": "text"},
            {"name": "sections", "label": "Секция", "type": "text"}
        ]
    },
    "Тренировки": {
        "base_query": """
            SELECT tr.id, g.name_ as group_name, s.name_ as section_name,
                   tr.day_of_the_week, tr.start_time, tr.end_time, tr.location_,
                   CONCAT(t.name_, ' ', t.surname) as trainer_name,
                   COUNT(DISTINCT a.tourist_id) as attendance_count
            FROM Trainings tr
            LEFT JOIN Groups_ g ON tr.group_id = g.id
            LEFT JOIN Sections s ON g.section_id = s.id
            LEFT JOIN Trainers t ON tr.trainer_id = t.id
            LEFT JOIN Attendance a ON tr.id = a.training_id
            GROUP BY tr.id
        """,
        "filters": [
            {"name": "group_name", "label": "Группа", "type": "text"},
            {"name": "section_name", "label": "Секция", "type": "text"},
            {"name": "day_of_the_week", "label": "День недели", "type": "select",
             "options": ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]},
            {"name": "trainer_name", "label": "Тренер", "type": "text"},
            {"name": "start_time", "label": "Время начала", "type": "time"},
            {"name": "location_", "label": "Локация", "type": "text"}
        ]
    },
    "Походы": {
        "base_query": """
            SELECT t.id, r.name_ as route_name, 
                   t.start_date, t.end_date, t.status, t.notes,
                   CONCAT(i.name_, ' ', i.surname) as instructor,
                   COUNT(DISTINCT tp.tourist_id) as participants_count,
                   GROUP_CONCAT(DISTINCT s.name_) as sections
            FROM Trips t
            LEFT JOIN Routes r ON t.route_id = r.id
            LEFT JOIN Tourists i ON t.instructor_id = i.id
            LEFT JOIN TripParticipants tp ON t.id = tp.trip_id
            LEFT JOIN Tourists tr ON tp.tourist_id = tr.id
            LEFT JOIN GroupParticipants gp ON tr.id = gp.tourist_id
            LEFT JOIN Groups_ g ON gp.group_id = g.id
            LEFT JOIN Sections s ON g.section_id = s.id
            GROUP BY t.id
        """,
        "filters": [
            {"name": "route_name", "label": "Маршрут", "type": "text"},
            {"name": "start_date", "label": "Дата начала", "type": "date"},
            {"name": "status", "label": "Статус", "type": "select",
             "options": ["планируется", "в процессе", "завершён"]},
            {"name": "instructor", "label": "Инструктор", "type": "text"},
            {"name": "sections", "label": "Секция", "type": "text"}
        ]
    },
    "Маршруты": {
        "base_query": """
            SELECT r.id, r.name_, r.type_, r.difficulty_category, 
                   r.total_length, r.estimated_days, r.description,
                   COUNT(DISTINCT rp.location_id) as points_count,
                   COUNT(DISTINCT t.id) as trips_count
            FROM Routes r
            LEFT JOIN RoutePoints rp ON r.id = rp.route_id
            LEFT JOIN Trips t ON r.id = t.route_id
            GROUP BY r.id
        """,
        "filters": [
            {"name": "name_", "label": "Название", "type": "text"},
            {"name": "type_", "label": "Тип", "type": "select",
             "options": ["пеший", "велосипедный", "водный"]},
            {"name": "difficulty_category", "label": "Сложность", "type": "select",
             "options": ["низкая", "средняя", "высокая"]},
            {"name": "total_length", "label": "Длина (км)", "type": "number"},
            {"name": "estimated_days", "label": "Дней", "type": "number"}
        ]
    },
    "Руководители": {
        "base_query": """
            SELECT l.id, l.name_, l.surname, l.patronymic, l.gender, l.age,
                   l.salary, l.date_of_birth, l.year_of_entry_into_employment,
                   s.name_ as section_name
            FROM Leaders l
            LEFT JOIN Sections s ON l.id = s.leader_id
        """,
        "filters": [
            {"name": "surname", "label": "Фамилия", "type": "text"},
            {"name": "gender", "label": "Пол", "type": "select", "options": ["мужской", "женский"]},
            {"name": "age", "label": "Возраст", "type": "number"},
            {"name": "salary", "label": "Зарплата", "type": "number"},
            {"name": "year_of_entry_into_employment", "label": "Год приема", "type": "text"},
            {"name": "section_name", "label": "Секция", "type": "text"}
        ]
    },
    "Посещаемость": {
        "base_query": """
            SELECT a.id, 
                   CONCAT(t.name_, ' ', t.surname) as tourist_name,
                   g.name_ as group_name,
                   s.name_ as section_name,
                   a.date_, 
                   tr.day_of_the_week, tr.start_time, tr.end_time,
                   a.is_present
            FROM Attendance a
            JOIN Tourists t ON a.tourist_id = t.id
            JOIN Trainings tr ON a.training_id = tr.id
            LEFT JOIN Groups_ g ON tr.group_id = g.id
            LEFT JOIN Sections s ON g.section_id = s.id
        """,
        "filters": [
            {"name": "tourist_name", "label": "Турист", "type": "text"},
            {"name": "group_name", "label": "Группа", "type": "text"},
            {"name": "section_name", "label": "Секция", "type": "text"},
            {"name": "date_", "label": "Дата", "type": "date"},
            # {"name": "day_of_the_week", "label": "День недели", "type": "select",
            #  "options": ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]},
            {"name": "is_present", "label": "Присутствие", "type": "select", "options": ["True", "False"]}
        ]
    }
}


@app.route('/filters/<table>')
def show_filters(table):
    if table not in FILTER_CONFIG:
        abort(404)
    return render_template('filters.html',
                           table=table,
                           filter_fields=FILTER_CONFIG[table]["filters"])


@app.route('/apply_filters/<table>', methods=['POST'])
def apply_filters(table):
    if table not in FILTER_CONFIG:
        abort(404)

    filters = []
    params = []

    for field in FILTER_CONFIG[table]["filters"]:
        filter_type = request.form.get(f"filter_type_{field['name']}")
        filter_value = request.form.get(f"filter_value_{field['name']}")

        if not filter_value:
            continue

        field_name = field['name']
        field_type = field.get('type', 'text')

        if field.get('options') and filter_value not in field['options']:
            continue

        if field_type == 'date':
            try:
                if filter_type == 'eq':
                    filters.append(f"{field_name}::date = %s")
                    params.append(filter_value)
                elif filter_type == 'gt':
                    filters.append(f"{field_name}::date > %s")
                    params.append(filter_value)
                elif filter_type == 'lt':
                    filters.append(f"{field_name}::date < %s")
                    params.append(filter_value)
            except ValueError:
                continue
        elif field_type == 'number':
            try:
                num_value = float(filter_value)
                if filter_type == 'eq':
                    filters.append(f"{field_name} = %s")
                    params.append(num_value)
                elif filter_type == 'gt':
                    filters.append(f"{field_name} > %s")
                    params.append(num_value)
                elif filter_type == 'lt':
                    filters.append(f"{field_name} < %s")
                    params.append(num_value)
            except ValueError:
                continue
        else:
            if filter_type == 'eq':
                filters.append(f"{field_name} = %s")
                params.append(filter_value)
            elif filter_type == 'gt':
                filters.append(f"{field_name} > %s")
                params.append(filter_value)
            elif filter_type == 'lt':
                filters.append(f"{field_name} < %s")
                params.append(filter_value)
            elif filter_type == 'like':
                filters.append(f"{field_name} ILIKE %s")
                params.append(f"%{filter_value}%")

    query = FILTER_CONFIG[table]["base_query"]
    if filters:
        query += " WHERE " + " AND ".join(filters)

    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()
        headers = [desc[0] for desc in cur.description]
        return render_template('filter_results.html',
                               table=table,
                               headers=headers,
                               rows=rows)
    except Exception as e:
        return f"Ошибка при выполнении запроса: {e}"
    finally:
        cur.close()
        conn.close()


def get_english_table_name(russian_name):
    return TABLE_NAME_MAPPING.get(russian_name, russian_name)


def get_russian_table_name(english_name):
    return REVERSE_TABLE_MAPPING.get(english_name, english_name)


def check_access(table, action):
    user_role = session.get('user', {}).get('role')

    if user_role == 'guest' and action != 'view':
        abort(403)

    elif user_role == 'employee':
        allowed_tables = [
            "Посещаемость", "Тренировки", "Группы",
            "Attendance", "Trainings", "Groups_"
        ]

        english_name = TABLE_NAME_MAPPING.get(table, table)
        if table not in allowed_tables and english_name not in allowed_tables:
            abort(403)

    elif user_role == 'admin':
        return

    else:
        abort(403)


@app.route('/edit/<table>/<int:record_id>', methods=['GET', 'POST'])
def edit_entry(table, record_id):
    check_access(table, 'edit')
    if table not in TABLES_META:
        return "Таблица не найдена", 404

    table_name = get_english_table_name(
        table if table in TABLES_META else REVERSE_TABLE_MAPPING.get(table, table)).lower()

    meta = None
    for t in TABLES_META.values():
        if t.get("table_name", "").lower() == table_name:
            meta = t
            break
    if not meta:
        abort(404, description="Метаданные таблицы не найдены")

    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()

    try:
        cur.execute(f"SELECT EXISTS(SELECT 1 FROM {meta['table_name']} WHERE id = %s)", (record_id,))
        if not cur.fetchone()[0]:
            abort(404, description="Запись не найдена")

        if request.method == 'POST':
            update_fields = []
            update_values = []
            for field in meta["fields"]:
                val = request.form.get(field["name"])
                update_fields.append(f"{field['name']} = %s")
                update_values.append(val)

            update_values.append(record_id)
            update_query = f"""
                UPDATE {meta['table_name']} 
                SET {', '.join(update_fields)} 
                WHERE id = %s
            """
            cur.execute(update_query, update_values)
            conn.commit()
            return redirect(url_for('index'))

        cur.execute(f"SELECT * FROM {meta['table_name']} WHERE id = %s", (record_id,))
        record = cur.fetchone()
        colnames = [desc[0] for desc in cur.description]
        record_dict = dict(zip(colnames, record))

        fk_options = {}
        for field in meta["fields"]:
            if field["type"] == "select" and "options_query" in field:
                try:
                    cur.execute(field["options_query"])
                    fk_options[field["name"]] = cur.fetchall()
                except Exception as e:
                    print(f"Ошибка при выполнении запроса опций: {e}")
                    fk_options[field["name"]] = []

        return render_template('edit_form.html',
                               table=table,
                               fields=meta["fields"],
                               record=record_dict,
                               fk_options=fk_options)

    except Exception as e:
        conn.rollback()
        print(f"Ошибка: {str(e)}")
        abort(500, description=f"Ошибка сервера: {str(e)}")
    cur.close()
    conn.close()


@app.route('/add/<table>', methods=['GET', 'POST'])
def add_entry(table):
    check_access(table, 'add')
    if table not in TABLES_META:
        return "Таблица не найдена", 404

    meta = TABLES_META[table]

    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()

    if request.method == 'POST':
        values = []
        columns = []
        placeholders = []
        for field in meta["fields"]:
            val = request.form.get(field["name"])
            if val is None:
                val = None
            columns.append(field["name"])
            placeholders.append('%s')
            values.append(val)

        query = f"INSERT INTO {meta['table_name']} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        cur.execute(query, values)
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/')

    options_data = {}
    for field in meta["fields"]:
        if field["type"] == "select" and "options_query" in field:
            cur.execute(field["options_query"])
            options_data[field["name"]] = cur.fetchall()

    cur.close()
    conn.close()
    return render_template('add_form.html', table=table, meta=meta, options_data=options_data, record={})


def has_permission(table_name, action):
    role = session.get("user", {}).get("role")

    if role == 'admin':
        return True

    if role == 'employee':
        allowed = ["Посещаемость", "Тренировки", "Группы",
                   "Attendance", "Trainings", "Groups_"]
        return table_name in allowed

    if role == 'guest':
        return action == 'view'

    return False


@app.route("/delete/<table>/<int:row_id>", methods=["POST"])
def delete_entry(table, row_id):
    check_access(table, 'delete')
    try:
        meta = None
        if table in TABLES_META:
            meta = TABLES_META[table]
        else:
            for t_meta in TABLES_META.values():
                if t_meta.get("table_name", "").lower() == table.lower():
                    meta = t_meta
                    break

        if not meta:
            abort(404, description=f"Таблица '{table}' не найдена в метаданных")

        db_table_name = meta["table_name"]

        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()

        cur.execute(f"SELECT 1 FROM {db_table_name} WHERE id = %s", (row_id,))
        if not cur.fetchone():
            abort(404, description=f"Запись с ID {row_id} не найдена в таблице {db_table_name}")

        cur.execute(f"DELETE FROM {db_table_name} WHERE id = %s", (row_id,))
        conn.commit()

        return redirect(url_for('index'))

    except psycopg2.IntegrityError as e:
        conn.rollback()
        abort(400, description=f"Ошибка целостности данных: {str(e)}")
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Ошибка при удалении: {str(e)}")
        abort(500, description="Внутренняя ошибка сервера")
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('role')
        if role == 'guest':
            login_as_guest()
            return redirect('/')
        else:
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            patronymic = request.form['patronymic']
            if role == 'employee':
                if login_as_employee(first_name, last_name, patronymic):
                    return redirect('/')
            elif role == 'admin':
                if login_as_admin(first_name, last_name, patronymic):
                    return redirect('/')
            return "Неверные данные или доступ запрещён"
    return render_template('login.html')


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route("/", methods=["GET", "POST"])
def index():
    if 'user' not in session or 'role' not in session['user']:
        return redirect('/login')
    tables = list(TABLE_QUERIES.keys())
    selected_table = None
    rows = []
    headers = []

    if request.method == "POST":
        selected_table = request.form.get("table")
        query = TABLE_QUERIES.get(selected_table)

        if query:
            try:
                conn = psycopg2.connect(**conn_params)
                cur = conn.cursor()
                cur.execute(query)
                rows = cur.fetchall()
                headers = [desc[0] for desc in cur.description]
                cur.close()
                conn.close()
            except Exception as e:
                return f"Ошибка при выполнении запроса: {e}"

    return render_template("index.html", tables=tables, selected_table=selected_table,
                           rows=rows, headers=headers, editable_tables=EDITABLE_TABLES)


app.jinja_env.globals.update(has_permission=has_permission)
if __name__ == "__main__":
    app.run(debug=True)
