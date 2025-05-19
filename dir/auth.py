from flask import session
from db import get_db_connection

def login_as_employee(first_name, last_name, patronymic):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT tc.category
        FROM Tourists t
        JOIN TouristCategories tc ON tc.id = t.category_id
        WHERE t.name_ = %s AND t.surname = %s AND t.patronymic = %s
    """, (first_name, last_name, patronymic))

    row = cursor.fetchone()
    cursor.close()

    if row and row[0] in ('спортсмен', 'тренер'):
        session['user'] = {
            'role': 'employee',
            'first_name': first_name,
            'last_name': last_name,
            'patronymic': patronymic
        }
        return True
    return False

def login_as_admin(first_name, last_name, patronymic):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 1 FROM Leaders
        WHERE name_ = %s AND surname = %s AND patronymic = %s
    """, (first_name, last_name, patronymic))

    row = cursor.fetchone()
    cursor.close()

    if row:
        session['user'] = {
            'role': 'admin',
            'first_name': first_name,
            'last_name': last_name,
            'patronymic': patronymic
        }
        return True
    return False

def login_as_guest():
    session['user'] = {
        'role': 'guest'
    }

def get_current_user_role():
    return session.get('user', {}).get('role', 'guest')
