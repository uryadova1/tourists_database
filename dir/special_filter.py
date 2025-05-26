SPECIAL_FILTER = {
    "Специальные запросы": {
        "base_query": "",
        "special_queries": {
            "tourists_by_criteria": {
                "name": "Фильтр туристов",
                "description": "Поиск туристов по секции, группе, полу, возрасту и году рождения",
                "fields": [
                    {
                        "name": "section_name",
                        "label": "Секция",
                        "type": "select",
                        "options_query": "SELECT DISTINCT name_ FROM Sections ORDER BY name_"
                    },
                    {
                        "name": "group_name",
                        "label": "Группа",
                        "type": "select",
                        "options_query": "SELECT DISTINCT name_ FROM Groups_ ORDER BY name_"
                    },
                    {
                        "name": "gender",
                        "label": "Пол",
                        "type": "select",
                        "options": ["мужской", "женский"]
                    },
                    {
                        "name": "birth_year",
                        "label": "Год рождения",
                        "type": "number",
                        "min": 1900,
                        "max": 2100
                    },
                    {
                        "name": "age",
                        "label": "Возраст",
                        "type": "number",
                        "min": 0,
                        "max": 120
                    }
                ],
                "query": """
                SELECT 
                    t.id,
                    t.surname,
                    t.name_,
                    t.patronymic,
                    t.gender,
                    t.age,
                    TO_CHAR(t.date_of_birth, 'YYYY-MM-DD') AS birth_date,
                    tc.category AS tourist_category,
                    s.name_ AS section_name,
                    g.name_ AS group_name
                FROM Tourists t
                JOIN TouristCategories tc ON tc.id = t.category_id
                JOIN GroupParticipants gp ON gp.tourist_id = t.id
                JOIN Groups_ g ON g.id = gp.group_id
                JOIN Sections s ON s.id = g.section_id
                WHERE
                    (%(section_name)s IS NULL OR s.name_ = %(section_name)s) AND
                    (%(group_name)s IS NULL OR g.name_ = %(group_name)s) AND
                    (%(gender)s IS NULL OR t.gender = %(gender)s) AND
                    (%(birth_year)s IS NULL OR EXTRACT(YEAR FROM t.date_of_birth) = %(birth_year)s) AND
                    (%(age)s IS NULL OR t.age = %(age)s)
                ORDER BY t.surname, t.name_
            """
            },

            "trainers_by_criteria": {
                "name": "Фильтр тренеров",
                "description": "Поиск тренеров по секции, полу, возрасту, зарплате и специализации",
                "fields": [
                    {
                        "name": "section_name",
                        "label": "Секция",
                        "type": "select",
                        "options_query": "SELECT DISTINCT name_ FROM Sections ORDER BY name_"
                    },
                    {
                        "name": "gender",
                        "label": "Пол",
                        "type": "select",
                        "options": ["мужской", "женский"]
                    },
                    {
                        "name": "min_age",
                        "label": "Минимальный возраст",
                        "type": "number",
                        "min": 18,
                        "max": 100
                    },
                    {
                        "name": "min_salary",
                        "label": "Минимальная зарплата",
                        "type": "number",
                        "min": 0
                    },
                    {
                        "name": "specialization",
                        "label": "Специализация",
                        "type": "select",
                        "options_query": "SELECT DISTINCT specialization FROM Trainers ORDER BY specialization"
                    }
                ],
                "query": """
                SELECT DISTINCT
                    tr.id AS trainer_id,
                    CONCAT(t.surname, ' ', t.name_, ' ', t.patronymic) AS full_name,
                    t.gender,
                    t.age,
                    tr.salary,
                    tr.specialization,
                    s.name_ AS section_name,
                    (SELECT STRING_AGG(g.name_, ', ') FROM Groups_ g WHERE g.trainer_id = tr.id) AS groups_led
                FROM Trainers tr
                JOIN Tourists t ON t.id = tr.tourist_id
                JOIN Groups_ g ON g.trainer_id = tr.id
                JOIN Sections s ON s.id = g.section_id
                WHERE
                    (%(section_name)s IS NULL OR s.name_ = %(section_name)s) AND
                    (%(gender)s IS NULL OR t.gender = %(gender)s) AND
                    (%(min_age)s IS NULL OR t.age >= %(min_age)s) AND
                    (%(min_salary)s IS NULL OR tr.salary >= %(min_salary)s) AND
                    (%(specialization)s IS NULL OR tr.specialization = %(specialization)s)
                ORDER BY tr.salary DESC
            """
            },

            "routes_by_location_and_difficulty": {
                "name": "Маршруты по точке и сложности",
                "description": "Поиск маршрутов, проходящих через точку, с длиной и категорией сложности",
                "fields": [
                    {
                        "name": "location_name",
                        "label": "Точка маршрута",
                        "type": "select",
                        "options_query": "SELECT DISTINCT name_ FROM Locations ORDER BY name_"
                    },
                    {
                        "name": "min_length",
                        "label": "Мин. длина (км)",
                        "type": "number",
                        "min": 0,
                        "step": 0.1
                    },
                    {
                        "name": "difficulty_category",
                        "label": "Сложность",
                        "type": "select",
                        "options_query": "SELECT DISTINCT difficulty_category FROM Routes ORDER BY difficulty_category"
                    }
                ],
                "query": """
                SELECT 
                    r.id,
                    r.name_ AS route_name,
                    r.total_length,
                    r.difficulty_category,
                    (SELECT STRING_AGG(l.name_, ', ') 
                     FROM RoutePoints rp 
                     JOIN Locations l ON l.id = rp.location_id 
                     WHERE rp.route_id = r.id) AS locations
                FROM Routes r
                JOIN RoutePoints rp ON rp.route_id = r.id
                JOIN Locations l ON l.id = rp.location_id
                WHERE
                    (%(location_name)s IS NULL OR l.name_ = %(location_name)s) AND
                    (%(min_length)s IS NULL OR r.total_length >= %(min_length)s) AND
                    (%(difficulty_category)s IS NULL OR r.difficulty_category = %(difficulty_category)s)
                GROUP BY r.id
                ORDER BY r.total_length DESC
            """
            },

            "trainer_load_by_period": {
                "name": "Нагрузка тренеров",
                "description": "Получить нагрузку тренеров по видам занятий и за период",
                "fields": [
                    {
                        "name": "trainer_name",
                        "label": "Тренер",
                        "type": "select",
                        "options_query": """
                        SELECT DISTINCT CONCAT(t.surname, ' ', t.name_) AS full_name 
                        FROM Trainers tr 
                        JOIN Tourists t ON t.id = tr.tourist_id 
                        ORDER BY full_name
                    """
                    },
                    {
                        "name": "date_from",
                        "label": "Дата начала",
                        "type": "date"
                    },
                    {
                        "name": "date_to",
                        "label": "Дата окончания",
                        "type": "date"
                    }
                ],
                "query": """
                SELECT 
                t.id,
                CONCAT(t.surname, ' ', t.name_) AS full_name,
                s.name_ AS section_name,
                COUNT(DISTINCT train.id) AS training_count,
                SUM(ROUND(EXTRACT(EPOCH FROM (train.end_time - train.start_time)) / 3600.0, 2)) AS total_hours
            FROM Trainers tr
            JOIN Tourists t ON t.id = tr.tourist_id
            JOIN Trainings train ON train.trainer_id = tr.id
            JOIN Attendance a ON a.training_id = train.id
            JOIN Groups_ g ON g.id = train.group_id
            JOIN Sections s ON s.id = g.section_id
            WHERE
                (%(trainer_name)s IS NULL OR CONCAT(t.surname, ' ', t.name_) = %(trainer_name)s) AND
                a.date_ BETWEEN %(date_from)s AND %(date_to)s
            GROUP BY t.id, full_name, s.name_
            ORDER BY total_hours DESC
            """
            },

            "trip_participants_by_criteria": {
                "name": "Походы по критериям",
                "description": "Туристы, ходившие в походы по маршрутам, точкам, категориям, в период",
                "fields": [
                    {
                        "name": "section_name",
                        "label": "Секция",
                        "type": "select",
                        "options_query": "SELECT DISTINCT name_ FROM Sections ORDER BY name_"
                    },
                    {
                        "name": "group_name",
                        "label": "Группа",
                        "type": "select",
                        "options_query": "SELECT DISTINCT name_ FROM Groups_ ORDER BY name_"
                    },
                    {
                        "name": "category",
                        "label": "Категория туриста",
                        "type": "select",
                        "options_query": "SELECT DISTINCT category FROM TouristCategories ORDER BY category"
                    },
                    {
                        "name": "route_name",
                        "label": "Маршрут",
                        "type": "select",
                        "options_query": "SELECT DISTINCT name_ FROM Routes ORDER BY name_"
                    },
                    {
                        "name": "location_name",
                        "label": "Точка маршрута",
                        "type": "select",
                        "options_query": "SELECT DISTINCT name_ FROM Locations ORDER BY name_"
                    },
                    {
                        "name": "start_date",
                        "label": "Дата начала",
                        "type": "date"
                    },
                    {
                        "name": "end_date",
                        "label": "Дата окончания",
                        "type": "date"
                    },
                    {
                        "name": "min_trip_count",
                        "label": "Мин. походов",
                        "type": "number",
                        "min": 1
                    }
                ],
                "query": """
                SELECT 
                    t.id,
                    CONCAT(t.surname, ' ', t.name_) AS full_name,
                    tc.category AS tourist_category,
                    s.name_ AS section_name,
                    g.name_ AS group_name,
                    COUNT(DISTINCT tr.id) AS trip_count,
                    STRING_AGG(DISTINCT r.name_, ', ') AS route_names
                FROM Tourists t
                JOIN TouristCategories tc ON tc.id = t.category_id
                JOIN TripParticipants tp ON tp.tourist_id = t.id
                JOIN Trips tr ON tr.id = tp.trip_id
                JOIN Routes r ON r.id = tr.route_id
                JOIN Groups_ g ON EXISTS (
                    SELECT 1 FROM Trainings train
                    JOIN Attendance a ON a.training_id = train.id
                    WHERE a.tourist_id = t.id AND train.group_id = g.id
                )
                JOIN Sections s ON s.id = g.section_id
                WHERE
                    (%(section_name)s IS NULL OR s.name_ = %(section_name)s) AND
                    (%(group_name)s IS NULL OR g.name_ = %(group_name)s) AND
                    (%(category)s IS NULL OR tc.category = %(category)s) AND
                    (%(route_name)s IS NULL OR r.name_ = %(route_name)s) AND
                    (%(location_name)s IS NULL OR EXISTS (
                        SELECT 1 FROM RoutePoints rp 
                        WHERE rp.route_id = r.id AND rp.location_id = (
                            SELECT id FROM Locations WHERE name_ = %(location_name)s
                        )
                    )) AND
                    (%(start_date)s IS NULL OR tr.start_date >= %(start_date)s) AND
                    (%(end_date)s IS NULL OR tr.end_date <= %(end_date)s)
                GROUP BY t.id, tc.category, s.name_, g.name_
                HAVING COUNT(DISTINCT tr.id) >= %(min_trip_count)s
                ORDER BY trip_count DESC
            """
            },
            "competitions_by_section": {
                "name": "Соревнования по секциям",
                "description": "Поиск соревнований с участниками из указанной секции",
                "fields": [
                    {
                        "name": "section_name",
                        "label": "Секция",
                        "type": "select",
                        "options_query": "SELECT DISTINCT name_ FROM Sections ORDER BY name_"
                    }
                ],
                "query": """
                SELECT 
                    c.id,
                    c.name_ AS competition_name,
                    TO_CHAR(c.date, 'YYYY-MM-DD') AS competition_date,
                    c.location_,
                    (SELECT COUNT(DISTINCT cp.tourist_id) 
                     FROM CompetitionParticipants cp 
                     WHERE cp.competition_id = c.id) AS participants_count
                FROM Competitions c
                WHERE EXISTS (
                    SELECT 1 FROM CompetitionParticipants cp
                    JOIN Tourists t ON t.id = cp.tourist_id
                    JOIN GroupParticipants gp ON gp.tourist_id = t.id
                    JOIN Groups_ g ON g.id = gp.group_id
                    JOIN Sections s ON s.id = g.section_id
                    WHERE cp.competition_id = c.id
                    AND (%(section_name)s IS NULL OR s.name_ = %(section_name)s)
                )
                ORDER BY c.date DESC
            """
            },

            "trainings_by_group_and_period": {
                "name": "Тренировки по группе и периоду",
                "description": "Тренеры, проводившие тренировки в указанной группе за период",
                "fields": [
                    {
                        "name": "group_name",
                        "label": "Группа",
                        "type": "select",
                        "options_query": "SELECT DISTINCT name_ FROM Groups_ ORDER BY name_"
                    },
                    {
                        "name": "date_from",
                        "label": "Дата начала",
                        "type": "date"
                    },
                    {
                        "name": "date_to",
                        "label": "Дата окончания",
                        "type": "date"
                    }
                ],
                "query": """
                SELECT DISTINCT 
                    tr.id AS trainer_id,
                    CONCAT(t.surname, ' ', t.name_, ' ', t.patronymic) AS full_name,
                    COUNT(DISTINCT train.id) AS training_count,
                    SUM(EXTRACT(EPOCH FROM (train.end_time - train.start_time))/3600)::numeric(10,2) AS total_hours
                FROM Trainers tr
                JOIN Tourists t ON t.id = tr.tourist_id
                JOIN Trainings train ON train.trainer_id = tr.id
                JOIN Attendance a ON a.training_id = train.id
                JOIN Groups_ g ON g.id = train.group_id
                WHERE
                    g.name_ = %(group_name)s AND
                    a.date_ BETWEEN %(date_from)s AND %(date_to)s
                GROUP BY tr.id, full_name
                ORDER BY total_hours DESC
            """
            },

            "leaders_by_criteria": {
                "name": "Руководители секций",
                "description": "Фильтр по зарплате, возрасту, году рождения и трудоустройства",
                "fields": [
                    {
                        "name": "min_salary",
                        "label": "Мин. зарплата",
                        "type": "number",
                        "min": 0
                    },
                    {
                        "name": "min_age",
                        "label": "Мин. возраст",
                        "type": "number",
                        "min": 18,
                        "max": 100
                    },
                    {
                        "name": "birth_year",
                        "label": "Год рождения",
                        "type": "number",
                        "min": 1900,
                        "max": 2100
                    },
                    {
                        "name": "employment_year",
                        "label": "Год трудоустройства",
                        "type": "number",
                        "min": 1900,
                        "max": 2100
                    }
                ],
                "query": """
                SELECT 
                    l.id,
                    CONCAT(l.surname, ' ', l.name_, ' ', l.patronymic) AS full_name,
                    l.salary,
                    l.age,
                    TO_CHAR(l.date_of_birth, 'YYYY-MM-DD') AS birth_date,
                    TO_CHAR(l.year_of_entry_into_employment, 'YYYY') AS employment_year,
                    (SELECT STRING_AGG(s.name_, ', ') 
                     FROM Sections s 
                     WHERE s.leader_id = l.id) AS sections
                FROM Leaders l
                WHERE
                    (%(min_salary)s IS NULL OR l.salary >= %(min_salary)s) AND
                    (%(min_age)s IS NULL OR l.age >= %(min_age)s) AND
                    (%(birth_year)s IS NULL OR EXTRACT(YEAR FROM l.date_of_birth) = %(birth_year)s) AND
                    (%(employment_year)s IS NULL OR EXTRACT(YEAR FROM l.year_of_entry_into_employment) = %(employment_year)s)
                ORDER BY l.salary DESC
            """
            },

            "qualified_tourists": {
                "name": "Квалифицированные туристы",
                "description": "Поиск туристов по секции, группе и навыкам",
                "fields": [
                    {
                        "name": "section_name",
                        "label": "Секция",
                        "type": "select",
                        "options_query": "SELECT DISTINCT name_ FROM Sections ORDER BY name_"
                    },
                    {
                        "name": "group_name",
                        "label": "Группа",
                        "type": "select",
                        "options_query": "SELECT DISTINCT name_ FROM Groups_ ORDER BY name_"
                    },
                    {
                        "name": "skills_keywords",
                        "label": "Навыки (ключевые слова)",
                        "type": "text"
                    }
                ],
                "query": """
                SELECT 
                    t.id,
                    CONCAT(t.surname, ' ', t.name_) AS full_name,
                    t.skills,
                    s.name_ AS section_name,
                    g.name_ AS group_name,
                    (SELECT COUNT(DISTINCT tp.trip_id) 
                     FROM TripParticipants tp 
                     WHERE tp.tourist_id = t.id) AS trip_count
                FROM Tourists t
                JOIN GroupParticipants gp ON gp.tourist_id = t.id
                JOIN Groups_ g ON g.id = gp.group_id
                JOIN Sections s ON s.id = g.section_id
                WHERE
                    s.name_ = %(section_name)s AND
                    g.name_ = %(group_name)s AND
                    (
                    %(skills_keywords)s IS NULL  OR LOWER(COALESCE(t.skills, '')) LIKE '%%' || LOWER(%(skills_keywords)s) || '%%'
                )
                ORDER BY t.surname, t.name_
            """
            },

            "instructors_by_criteria": {
                "name": "Инструкторы по критериям",
                "description": "Инструкторы с категорией, прошедшие маршруты и точки",
                "fields": [
                    {
                        "name": "category",
                        "label": "Категория",
                        "type": "select",
                        "options_query": "SELECT DISTINCT category FROM TouristCategories WHERE category IN ('спортсмен', 'тренер') ORDER BY category"
                    },
                    {
                        "name": "route_name",
                        "label": "Маршрут",
                        "type": "select",
                        "options_query": "SELECT DISTINCT name_ FROM Routes ORDER BY name_"
                    },
                    {
                        "name": "location_name",
                        "label": "Точка маршрута",
                        "type": "select",
                        "options_query": "SELECT DISTINCT name_ FROM Locations ORDER BY name_"
                    },
                    {
                        "name": "min_trip_count",
                        "label": "Мин. походов",
                        "type": "number",
                        "min": 1
                    }
                ],
                "query": """
                SELECT 
                    t.id,
                    CONCAT(t.surname, ' ', t.name_) AS full_name,
                    tc.category,
                    COUNT(DISTINCT tr.id) AS trip_count,
                    STRING_AGG(DISTINCT r.name_, ', ') AS routes
                FROM Tourists t
                JOIN TouristCategories tc ON tc.id = t.category_id
                JOIN Trips tr ON tr.instructor_id = t.id
                JOIN Routes r ON r.id = tr.route_id
                WHERE
                    tc.category = %(category)s AND
                    (%(route_name)s IS NULL OR r.name_ = %(route_name)s) AND
                    (%(location_name)s IS NULL OR EXISTS (
                        SELECT 1 FROM RoutePoints rp 
                        WHERE rp.route_id = r.id AND rp.location_id = (
                            SELECT id FROM Locations WHERE name_ = %(location_name)s
                        )
                    ))
                GROUP BY t.id, tc.category
                HAVING COUNT(DISTINCT tr.id) >= %(min_trip_count)s
                ORDER BY trip_count DESC
            """
            },

            "tourists_with_their_trainer": {
                "name": "Туристы с тренером",
                "description": "Туристы, ходившие в походы со своим тренером как инструктором",
                "fields": [],
                "query": """
                SELECT DISTINCT 
                t.id,
                CONCAT(t.surname, ' ', t.name_, ' ', t.patronymic) AS full_name
            FROM Tourists t
            JOIN TripParticipants tp ON tp.tourist_id = t.id
            JOIN Trips trip ON trip.id = tp.trip_id
            WHERE trip.instructor_id = (
                SELECT t2.id 
                FROM Trainers tr
                JOIN Tourists t2 ON t2.id = tr.tourist_id
                WHERE tr.id = (
                    SELECT g.trainer_id
                    FROM Groups_ g
                    JOIN Trainings trn ON trn.group_id = g.id
                    JOIN Attendance a ON a.training_id = trn.id
                    WHERE a.tourist_id = t.id
                    LIMIT 1
                )
            );

            """
            }

        }
    }

}
