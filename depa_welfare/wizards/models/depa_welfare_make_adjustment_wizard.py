from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date

class depa_welfare_make_adjustment_wizard(models.TransientModel):
    _name = 'depa_welfare_make_adjustment_wizard'

    welfare_line_id = fields.Many2one(
        'depa_welfare_lines'
    )

    remark = fields.Text(
        string="รายละเอียดการแก้ไข",
        help="กรอกเพื่อแสดงความคิดเห็น",
        required=True
    )

    is_adjustment = fields.Boolean(
        default=True
    )

    current_state = fields.Char()

    def action_save_adjustment(self):
        print(self)
        self.welfare_line_id.is_hr_reject = True
        self.welfare_line_id.memo_for_adjustment = self.remark

        return {
            'type': 'ir.actions.act_window_close'
        }
        # raise ValidationError(_('Not your turn'))

    def action_reject(self):
        raise ValidationError(_('Not your turn'))