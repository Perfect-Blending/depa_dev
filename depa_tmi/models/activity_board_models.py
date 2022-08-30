# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, datetime
from odoo.exceptions import UserError, ValidationError
from pytz import timezone
from dateutil.relativedelta import relativedelta

class activity_board_models(models.Model):
    _name = 'activity_board'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_employee_info(self):
        employee = self.env['hr.employee'].search([
            ('user_id', '=', self._uid)
        ], limit=1)
        return employee

    def _get_employee_id(self):
        employee = self.env['hr.employee'].search([
            ('user_id', '=', self._uid)
        ], limit=1)
        return employee.id

    def _get_all_state(self):
        states = self.env['leave_request_state'].search([
            ('active', '=', True)
        ])
        data = []
        for state in states:
            data.append((state.state, state.name))
        return data

    def _get_all_state_id(self, stages, domain, order):
        state_ids = self.env['leave_request_state'].search([])
        return state_ids

    def _get_state_id(self, state):
        state_record = self.env['leave_request_state'].search([
            ('state', '=', state)
        ], limit=1)
        if state_record:
            return state_record.id

    activity_name = fields.Char(
        string="ชื่อกิจกรรม"
    )

    employee_id = fields.Many2one(
        "hr.employee",
        string="ผู้ดำเนินการ",
        required=True,
        default= lambda self: self._get_employee_id()
    )

    approver_id = fields.Many2one(
        "hr.employee",
        string="ผู้อนุมัติ",
        required=True,
        default= lambda self: self._get_employee_info().parent_id
    )

    start_date = fields.Date(
        string="จากวันที่",
        required=True
    )

    end_date = fields.Date(
        string="ถึงวันที่",
        required=True
    )

    state = fields.Selection(
        # STATES,
        lambda self: self._get_all_state(),
        string="สถานะ",
        # default="to_do",
        copy=False,
        # track_visibility='onchange',
    )

    state_id = fields.Many2one(
        'leave_request_state',
        string="สถานะ",
        default=lambda self: self._get_state_id(state='draft'),
        group_expand='_get_all_state_id',
        track_visibility='onchange'
    )

    attachment_ids = fields.Many2many(
        "ir.attachment",
        "activity_board_attachment_rel",
        "activity_board_attachment_id",
        "ir_attachment_id",
        string="เอกสารแนบ"
    )

    approved_done = fields.Boolean(
        string="อนุมัติกิจกรรม",
        default=False,
    )

    # @api.onchange('state_id')
    # def onchange_state_id(self):
    #     raise ValidationError("TEST")
