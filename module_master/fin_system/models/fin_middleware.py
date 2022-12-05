from odoo import _
from datetime import datetime, date
import pytz


# def localized_datetime(self, odoodatetime):
#     user = self.env['res.users'].browse(self._uid)
#     if user.tz:
#         tz = pytz.timezone(user.tz) or pytz.utc
#         localize_datetime = pytz.utc.localize(odoodatetime).astimezone(tz)
#     else:
#         localize_datetime = odoodatetime
#     localize_datetime = localize_datetime.strftime("%d/%m/%Y, %H:%M:%S")
#     return localize_datetime

def message_log_stamp(self, action_name, odoodatetime):
    employee_obj = self.env['hr.employee'].search([
        ('user_id', '=', self._uid),
    ])
    if employee_obj:
        user_name = _("%s" % employee_obj.name)
    else:
        user_obj = self.env['res.users'].search([
            ('id', '=', self._uid),
        ])
        user_name = _("%s" % user_obj.name)

    user = self.env['res.users'].browse(self._uid)
    if user.tz:
        tz = pytz.timezone(user.tz) or pytz.utc
        localize_datetime = pytz.utc.localize(odoodatetime).astimezone(tz)
    else:
        localize_datetime = odoodatetime
    localize_datetime = localize_datetime.strftime("%d/%m/%Y, %H:%M:%S")

    message = (
        "<b><u>%s</u></b><br />%s : <b>%s</b><br />Action : %s <br />Date/Time : %s" % (
        "SYSTEM LOG",
        "Employee" if employee_obj else "User",
        str(user_name),
        str(action_name),
        str(localize_datetime),
    ))
    return message