# staff_management/utils.py


from .models import SystemSetting

def is_backdate_allowed():
    return SystemSetting.get_instance().allow_backdate