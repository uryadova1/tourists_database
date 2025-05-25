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
            {"name": "is_present", "label": "Присутствие", "type": "select", "options": ["True", "False"]}
        ]

    },
}
