from odoo import models, fields, api
from datetime import date
from odoo.exceptions import UserError, ValidationError

class kpi_behaviour_setting(models.Model):
    _name = 'kpi_behaviour_setting'

    def _default_fiscal_year(self):
        fiscal_year_obj = self.env['fw_pfb_fin_system_fiscal_year'].search([
            ('date_start', '<=', date.today()),
            ('date_end', '>=', date.today()),
        ], limit=1)
        if fiscal_year_obj:
            return fiscal_year_obj.id

    behaviour_year = fields.Many2one(
        'fw_pfb_fin_system_fiscal_year',
        default=_default_fiscal_year,
        required=True
    )
    behaviour_setting_lines_ids = fields.One2many(
        'kpi_behaviour_setting_lines',
        'behaviour_setting_lines_id',
        # required=True,
        copy=True
    )


class kpi_behaviour_setting_lines(models.Model):
    _name = 'kpi_behaviour_setting_lines'

    behaviour_desc = fields.Text(
        string='รายละเอียด'
    )
    behaviour_weight = fields.Float(
        string="น้ำหนัก",
        digits=(10, 2)
    )
    behaviour_type = fields.Selection(
        [
            ('operation', 'ปฏิบัติการ'),
            ('management', 'บริหาร')
        ],
        string="ประเภท",
        digits=(10, 2)
    )
    behaviour_unit =fields.Many2one(
        'uom.uom',
        'หน่วย'
    )
    behaviour_score = fields.Float(
        string='คะแนน',
        digits=(10, 2)
    )
    active = fields.Boolean(
        default=True
    )
    behaviour_setting_lines_id = fields.Many2one(
        'kpi_behaviour_setting',
        required=True,
        ondelete='cascade'
    )
    behaviour_definition_setting_lines_ids = fields.One2many(
        "behaviour_definition_setting_lines",
        "behaviour_definition_setting_lines_id",
        string="คำจำกัดความ",
        copy=True
    )

    @api.multi
    def name_get(self):
        return [(rec.id, rec.behaviour_desc) for i, rec in enumerate(self)]

    @api.model
    def name_search(self, name, args=None, operator='like', limit=100):
        if not args:
            args = []
        if name:
            result = self._search(args + [
                '|',
                ('behaviour_type', operator, name),
                ('behaviour_desc', operator, name),
            ])
        else:
            result = self._search(args, limit=limit)
        print(result)
        return self.browse(result).name_get()

class behaviour_definition_setting_lines(models.Model):
    _name = 'behaviour_definition_setting_lines'

    behaviour_definition_setting_lines_id = fields.Many2one(
        'kpi_behaviour_setting_lines',
        required=True,
        ondelete='cascade'
    )
    level = fields.Selection(
        [
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
            ('4', '4'),
            ('5', '5'),
        ],
        string="ระดับคะแนน",
        required=True
    )
    name = fields.Char(
        string="คำจำกัดความ",
        required=True
    )
    active = fields.Boolean(
        default=True
    )