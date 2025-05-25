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