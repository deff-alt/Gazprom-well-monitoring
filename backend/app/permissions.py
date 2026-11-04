"""
Централизованная матрица прав по ролям.

Использование в роутерах:
    from app.permissions import can_edit_wells, can_view_alerts
    if not can_edit_wells(current_user):
        raise HTTPException(403, "Недостаточно прав")
"""
from app.models import Role, User


# ===== Справочники =====

def can_edit_registry(user: User) -> bool:
    """CRUD по месторождениям, промыслам, скважинам."""
    return user.role in (Role.ADMIN, Role.ENGINEER)


def can_delete_registry(user: User) -> bool:
    """Удаление записей в справочниках (только админ)."""
    return user.role == Role.ADMIN


# ===== Телеметрия =====

def can_view_telemetry(user: User) -> bool:
    """Просмотр телеметрии. Все авторизованные."""
    return True


def can_configure_thresholds(user: User) -> bool:
    """Настройка порогов аномалий."""
    return user.role in (
        Role.ADMIN,
        Role.ENGINEER,
        Role.KIPIA_ENGINEER,
        Role.POWER_ENGINEER,
        Role.MECHANICAL_ENGINEER,
    )


# ===== Алерты =====

def can_view_alerts(user: User) -> bool:
    """Просмотр алертов. Все авторизованные."""
    return True


def can_work_with_alerts(user: User) -> bool:
    """Взять в работу, закрыть, назначить ответственного."""
    return user.role in (
        Role.ADMIN,
        Role.ENGINEER,
        Role.HEAD,
        Role.KIPIA_ENGINEER,
        Role.POWER_ENGINEER,
        Role.MECHANICAL_ENGINEER,
        Role.GEOLOGIST,
        Role.DISPATCHER,
    )


# ===== Производство =====

def can_edit_production(user: User) -> bool:
    """Замеры дебита."""
    return user.role in (Role.ADMIN, Role.ENGINEER, Role.GEOLOGIST)


def can_edit_workovers(user: User) -> bool:
    """Капремонты."""
    return user.role in (Role.ADMIN, Role.ENGINEER, Role.MECHANICAL_ENGINEER)


# ===== ML =====

def can_train_model(user: User) -> bool:
    """Переобучение ML-модели (только админ)."""
    return user.role == Role.ADMIN


def can_predict(user: User) -> bool:
    """Ручной запуск инференса."""
    return user.role in (
        Role.ADMIN,
        Role.ENGINEER,
        Role.KIPIA_ENGINEER,
        Role.MECHANICAL_ENGINEER,
        Role.GEOLOGIST,
    )


# ===== Пользователи =====

def can_manage_users(user: User) -> bool:
    """Управление пользователями."""
    return user.role == Role.ADMIN