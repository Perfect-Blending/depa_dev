# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime

class depa_welfare_hr(models.Model):
    _name = 'depa_welfare_hr'

    def _default_fiscal_year(self):
        fiscal_year_obj = self.env['fw_pfb_fin_system_fiscal_year'].search([
            ('date_start', '<=', date.today()),
            ('date_end', '>=', date.today()),
        ], limit=1)
        if fiscal_year_obj:
            return fiscal_year_obj.id

    year = fields.Many2one(
        'fw_pfb_fin_system_fiscal_year',
        default=_default_fiscal_year,
        required=True
    )
    # depa = fields.Boolean(
    #     string="depa",
    #     default=False,
    # )
    # gbdi = fields.Boolean(
    #     string="GBDi",
    #     default=False,
    # )
    depa_amount_total = fields.Float(
        compute="_depends_depa_amount_total",
        store=True,
        readonly=True
    )
    gbdi_amount_total = fields.Float(
        compute="_depends_gbdi_amount_total",
        store=True,
        readonly=True
    )
    amount_total = fields.Float(
        compute="_depends_amount_total",
        store=True,
        readonly=True
    )
    employee_ids = fields.One2many(
        'depa_welfare_hr_lines',
        'hr_employee_id',
        string='Employee',
        required=True,
        copy=True
    )
    is_create = fields.Boolean(default=True)

    @api.onchange('is_create')
    def _onchange_is_create(self):
        if self.is_create:
            fiscal_year_obj = self.env['fw_pfb_fin_system_fiscal_year'].search([
                ('date_start', '<=', date.today()),
                ('date_end', '>=', date.today()),
            ], limit=1)
            # print(fiscal_year_obj.id)
            depa_welfare_hr = self.env['depa_welfare_hr'].search([
                ('year', '=', fiscal_year_obj.id)
            ])
            #depa_welfare_hr_lines_id = self.env['depa_welfare_hr_lines'].search([('hr_employee_id', '=', depa_welfare_hr.id)])
            #employees = self.env['depa_welfare_hr_lines'].search([('hr_employee_id', '=', depa_welfare_hr.id)])
            # if employees:
            #     for emp in employees:
            #         self.employee_ids = [(1, 0, {
            #             'employee_id': [aa.id for aa in hr.employee],
            #             'point': emp.point,
            #             'amount': 105,
            #             'hr_employee_id': self.id,
            #         })]
            employee_obj = self.env['hr.employee'].search([])

            for emp in employee_obj:
                #print(emp.id)
                # self.employee_ids.create({
                #     'employee_id': emp.id,
                #     'point': 10,
                #     'hr_employee_id': self.id,
                # })
                self.employee_ids = [(0, 0, {
                    'employee_id': emp.id,
                    'employee_type': emp.employee_types,
                    'employee_department_id': emp.department_id,
                    'employee_department_name': emp.department_id.name,
                    'point': 315,
                    'hr_employee_id': self.id,
                })]

    @api.multi
    @api.depends('employee_ids.point')
    def _depends_amount_total(self):
        for welfare in self:
            amount_sum = 0
            for line in welfare.employee_ids:
                amount_sum += line.amount
            welfare.amount_total = amount_sum

    @api.depends('employee_ids.point')
    def _depends_depa_amount_total(self):
        for welfare in self:
            depa_amount_sum = 0
            for line in welfare.employee_ids:
                department = welfare.env["hr.department"].search([
                    ('id', '=', line.employee_id.department_id.id)
                ])
                if not department.is_gbdi:
                    depa_amount_sum += line.amount
            welfare.depa_amount_total = depa_amount_sum

    @api.depends('employee_ids.point')
    def _depends_gbdi_amount_total(self):
        for welfare in self:
            gbdi_amount_sum = 0
            for line in welfare.employee_ids:
                # if line.employee_department_id.is_gbdi:
                    # gbdi_amount_sum += line.amount
                department = welfare.env["hr.department"].search([
                    ('id', '=', line.employee_id.department_id.id)
                ])
                if department.is_gbdi:
                    gbdi_amount_sum += line.amount
            welfare.gbdi_amount_total = gbdi_amount_sum

    @api.model
    def create(self, vals):
        res = super(depa_welfare_hr, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        res = super(depa_welfare_hr, self).write(vals)
        return res

    @api.multi
    def unlink(self):
        for employee in self.employee_ids:
            employee_line = self.env["depa_welfare_hr_lines"].browse(employee.id)
            employee_line.unlink()
        return super(depa_welfare_hr, self).unlink()

    def action_draft_fin100_wizard(self):
        # print(self)
        return {
            'name': "Draft Fin100 Wizard",
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'depa_welfare_draft_fin100_wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_welfare_hr_id': self.id,
                'default_amount_total': self.amount_total,
                'default_price_unit': self.amount_total,
                'default_depa_amount_total': self.depa_amount_total,
                'default_depa_price_unit': self.depa_amount_total,
                'default_gbdi_amount_total': self.gbdi_amount_total,
                'default_gbdi_price_unit': self.gbdi_amount_total,
                # 'default_employee_id': employee_id.id,
                # 'default_setting_line': setting_line,
                # 'default_status': status,
                # 'default_total_for_approve': len(self.setting_line_ids) - count_nonactive,
                # 'default_setting_id': self.id,
            }
        }

EMP_TYPES = [
                ('operation', 'ระดับปฏิบัติการ'),
                ('academic', 'ระดับวิชาการ'),
                ('management', 'ระดับบริหาร'),
                ('temporary', 'ลูกจ้าง')
            ]

class SettingLine(models.Model):
    _name = 'depa_welfare_hr_lines'

    employee_id = fields.Many2one(
        'hr.employee',
        string="Employee Name"
    )
    employee_type = fields.Selection(
        EMP_TYPES
    )
    employee_department_id = fields.Many2one(
        'hr.department'
    )
    employee_department_name = fields.Char(
        string="สังกัด"
    )
    point = fields.Float(
        default=315
    )
    amount = fields.Float(
        compute="_depends_amount",
        store=True,
        readonly=True
    )
    hr_employee_id = fields.Many2one(
        'depa_welfare_hr',
        string="Document id",
        required=True,
    )
    is_sent_point_update = fields.Boolean(
        default=False
    )

    @api.depends('point', 'hr_employee_id.employee_ids')
    def _depends_amount(self):
        for line in self:
            line.amount = round(line.point, 2) * 105

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        self.employee_type = self.employee_id.employee_types
        self.employee_department_id = self.employee_id.department_id
        self.employee_department_name = self.employee_id.department_id.name

    @api.model
    def create(self, vals):
        new_point = vals['point']
        point_type = 'add'
        if new_point != 0:
            employee_id = vals['employee_id']
            # print(employee_id)
            depa_welfare_hr = self.env['depa_welfare_hr'].search([('id', '=', vals['hr_employee_id'])])

            point_history = {
                "desc": "ตั้งค่า Point จากผู้ดูแลระบบ",
                "on_date": datetime.now(),
                "point_type": point_type,
                "point_usage": new_point,
                "point_balance": new_point,
                "employee_id": employee_id,
                "welfare_fiscal_year": depa_welfare_hr.year.id
            }
            self.env['point_history_lines'].create(point_history)

        res = super(SettingLine, self).create(vals)
        return res

    @api.multi
    def write(self, vals):

        if not 'is_sent_point_update' in vals:
            for index, rec in enumerate(self):
                if 'point' in vals:
                    employee_id = rec.employee_id.id
                    prev_point = point_usage = rec.point
                    new_point = vals['point']
                    point_type = ''

                    if new_point != prev_point:
                        if new_point > prev_point:
                            point_usage = new_point - prev_point
                            point_type = 'add'
                        elif new_point < prev_point:
                            point_usage = prev_point - new_point
                            point_type = 'minus'

                        # Save to point history lines
                        point_history = {
                            "desc": "ตั้งค่า Point จากผู้ดูแลระบบ",
                            "on_date": datetime.now(),
                            "point_type": point_type,
                            "point_usage": point_usage,
                            "point_balance": new_point,
                            "employee_id": employee_id,
                            "welfare_fiscal_year": rec.hr_employee_id.year.id
                        }
                        self.env['point_history_lines'].create(point_history)

        vals['is_sent_point_update'] = False

        res = super(SettingLine, self).write(vals)
        return res
