from dir.auth import get_current_user_role


def can_view():
    return True  # все могут просматривать

def can_edit_section_table():
    role = get_current_user_role()
    return role in ['employee', 'admin']

def can_edit_all_tables():
    return get_current_user_role() == 'admin'
