# Copyright (C) 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api

from datetime import datetime, date
from dateutil.relativedelta import relativedelta


class HrEmployeeRelative(models.Model):
    _name = 'hr.employee.relative'
    _description = 'HR Employee Relative'

    def _get_age_round_up(self, dob):
        round_up = 0
        age = relativedelta(date.today(), dob)
        if age.months > 0 or age.days > 0:
            round_up = 1
        return age.years + round_up

    employee_id = fields.Many2one(
        string='Employee',
        comodel_name='hr.employee',
    )
    relation = fields.Selection(
        string='Relation',
        selection=[
            ('MO', 'มารดา'),
            ('FA', 'บิดา'),
            ('SP', 'คู่สมรส'),
            ('CH', 'บุตร'),
        ],
        required=True,
    )
    identify_number = fields.Char(
        string='Identification Number',
        size=13,
        required=True,
    )
    title_name = fields.Many2one(
        'hr.employee.title',
        string='Title name',
        required=True,
    )
    # relation_id = fields.Many2one(
    #     'hr.employee.relative.relation',
    #     string='Relation',
    #     required=True,
    # )
    name = fields.Char(
        string='Name',
        required=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        domain=[
            '&', ('is_company', '=', False), ('type', '=', 'contact')
        ],
    )
    gender = fields.Selection(
        string='Gender',
        selection=[
            ('male', 'ชาย'),
            ('female', 'หญิง'),
            # ('other', 'Other'),
        ],
        required=True,
    )
    date_of_birth = fields.Date(
        string='Date of Birth',
        required=True,
    )
    age = fields.Char(
        compute='_compute_age',
    )
    age_now = fields.Integer(
        compute='_compute_age_now',
        store=True
    )
    age_round_up = fields.Integer(
        compute='_compute_age_round_up',
        store=True
    )
    job = fields.Char()
    phone_number = fields.Char()

    notes = fields.Text(
        string='Notes',
    )

    @api.depends('date_of_birth')
    def _compute_age(self):
        for record in self:
            age = relativedelta(date.today(), record.date_of_birth)
            record.age = f"{age.years} ปี {age.months} เดือน {age.days} วัน"

    @api.depends('date_of_birth')
    def _compute_age_now(self):
        for record in self:
            age = relativedelta(date.today(), record.date_of_birth)
            record.age_now = age.years

    @api.depends('date_of_birth')
    def _compute_age_round_up(self):
        for record in self:
            record.age_round_up = self._get_age_round_up(record.date_of_birth)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.name = self.partner_id.display_name
