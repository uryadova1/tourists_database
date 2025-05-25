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