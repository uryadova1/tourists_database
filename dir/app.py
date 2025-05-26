from flask import Flask, render_template, request, redirect, session, url_for, abort
import psycopg2
from table_queries import TABLE_QUERIES
from table_meta import TABLES_META
from filter_config import FILTER_CONFIG
from special_filter import SPECIAL_FILTER

from auth import login_as_guest, login_as_employee, login_as_admin

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


# @app.route('/special_filters')
# def special_filters():
#     return render_template('special_filters.html',
#                            special_queries=SPECIAL_FILTER["Специальные запросы"]["special_queries"])


@app.route('/special_filters')
def special_filters():
    # Скопируем фильтры, чтобы не портить оригинальный словарь (опционально)
    import copy
    special_queries = copy.deepcopy(SPECIAL_FILTER["Специальные запросы"]["special_queries"])

    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()

        for query_data in special_queries.values():
            for field in query_data["fields"]:
                if field.get("type") == "select" and "options_query" in field:
                    cur.execute(field["options_query"])
                    field["options"] = [row[0] for row in cur.fetchall()]

    except Exception as e:
        return f"Ошибка при загрузке вариантов выбора: {e}"
    finally:
        cur.close()
        conn.close()

    return render_template('special_filters.html', special_queries=special_queries)


@app.route('/apply_special_filter/<query_key>', methods=['POST'])
def apply_special_filter(query_key):
    special_queries = SPECIAL_FILTER["Специальные запросы"]["special_queries"]
    if query_key not in special_queries:
        abort(404)

    query_data = special_queries[query_key]
    filters = {}

    for field in query_data['fields']:
        value = request.form.get(field['name'])
        if value == '':
            value = None  # ← добавь это!
        if value:
            if field['name'] == 'skills_keywords':  # ключевое поле
                filters[field['name']] = f"%{value}%"
            elif field['type'] == 'number':
                try:
                    filters[field['name']] = float(value)
                except ValueError:
                    pass
            else:
                filters[field['name']] = value
            if field['type'] == 'number':
                try:
                    filters[field['name']] = float(value)
                except ValueError:
                    pass
            else:
                filters[field['name']] = value
        else:
            filters[field['name']] = None

    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()

        cur.execute(query_data['query'], filters)
        rows = cur.fetchall()
        headers = [desc[0] for desc in cur.description]

        count_query = query_data.get('count_query')
        total = None
        if count_query:
            cur.execute(count_query, filters)
            total = cur.fetchone()[0]

        return render_template('special_filter_results.html',
                               query_name=query_data['name'],
                               headers=headers,
                               rows=rows,
                               total=total)
    except Exception as e:
        return f"Ошибка при выполнении запроса: {e}"
    finally:
        cur.close()
        conn.close()


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
