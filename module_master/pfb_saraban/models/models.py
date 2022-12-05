from odoo import models, fields, api, _
from datetime import timedelta
from odoo import ValidationError
class setting(models.Model):
    _name = 'document.setting'
    _description = 'สารบัญ'

    name = fields.Char(
        string='ชื่อ',
        required=True,
    )
    description = fields.Text(
        string='Description',
    )
    responsible_id = fields.Many2one(
        comodel_name='res.users',
        string="Responsible",
        ondelete='set null',
        index=True,
    )
    session_id = fields.One2many(
        comodel_name='res.partner',
        inverse_name='name',
        string='Sessions',
    )
   
    @api.multi
    def copy(self, default=None):
        default = dict(default or {})
        copied_count = self.search_count(
            [('name', '=like', _(u"Copy of {}%").format(self.name))])
        if not copied_count:
            new_name = _(u"Copy of {}").format(self.name)
        else:
            new_name = _(u"Copy of {} ({})").format(self.name, copied_count)

        default['name'] = new_name
        return super(setting, self).copy(default)

class SettingLine(models.Model):
    _name = 'document.setting.lines'
    _description = 'สารบัญ'
    employee_id= fields.Many2one(
        comodel_name='hr.employee',
        string="Employee"
    )
    document_id= fields.Many2one(
        comodel_name='hr.employee',
        string="Employee"
    )
    