from odoo import models, fields, api
from datetime import date
from odoo.exceptions import UserError, ValidationError

class kpi_contribution_setting(models.Model):
    _name = 'kpi_contribution_setting'

    def _default_fiscal_year(self):
        fiscal_year_obj = self.env['fw_pfb_fin_system_fiscal_year'].search([
            ('date_start', '<=', date.today()),
            ('date_end', '>=', date.today()),
        ], limit=1)
        if fiscal_year_obj:
            return fiscal_year_obj.id

    contribution_year = fields.Many2one(
        'fw_pfb_fin_system_fiscal_year',
        default=_default_fiscal_year,
        required=True
    )
    contribution_setting_lines_ids = fields.One2many(
        'kpi_contribution_setting_lines',
        'contribution_setting_lines_id',
        required=True,
        copy=True
    )

class kpi_contribution_setting_lines(models.Model):
    _name = 'kpi_contribution_setting_lines'

    contribution_code = fields.Char(
        string='รหัส'
    )
    contribution_desc = fields.Text(
        string='รายละเอียด'
    )
    contribution_unit =fields.Many2one(
        'uom.uom',
        'หน่วย'
    )
    contribution_score = fields.Float(
        string='คะแนน',
        digits=(10, 2)
    )
    active = fields.Boolean(
        default=True
    )
    contribution_setting_lines_id = fields.Many2one(
        'kpi_contribution_setting'
    )

    @api.multi
    def name_get(self):
        return [(rec.id, rec.contribution_code + ' ' + rec.contribution_desc) for i, rec in enumerate(self)]

    @api.model
    def name_search(self, name, args=None, operator='like', limit=100):
        if not args:
            args = []
        if name:
            result = self._search(args + [
                '|',
                ('contribution_code', operator, name),
                ('contribution_desc', operator, name),
            ])
        else:
            result = self._search(args, limit=limit)
        print(result)
        return self.browse(result).name_get()
