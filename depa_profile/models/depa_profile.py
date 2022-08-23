# -*- coding: utf-8 -*-
import base64

from odoo import api, fields, models
from odoo import tools, _
from datetime import datetime, date
from odoo.exceptions import UserError, ValidationError
from odoo.modules.module import get_module_resource

class depa_profile(models.Model):
    _inherit = 'hr.employee'

    employee_group_id = fields.Many2one(
        "depa_group",
        string="กลุ่มงาน",
        default=False
    )

    department_id_name = fields.Char(
        string="สังกัด",
        compute='_get_department_name',
        store=True,
        default=False
    )

    @api.depends('department_id')
    def _get_department_name(self):
        for rec in self:
            employee = self.env['hr.employee'].search([
                ('user_id', '=', rec._uid)
            ], limit=1)
            rec.department_id_name = employee.department_id.name
            rec.employee_group_id = employee.department_id.department_group_id



    # def get_current_res_id(self):
    #     context = self._context
    #     current_uid = context.get('uid')

    #     employee = self.sudo().env['hr.employee'].search([
    #         ('user_id', '=', current_uid)
    #     ], limit=1)

    #     return {
    #         "type": "ir.actions.act_window",
    #         "name": "ข้อมูลผู้ใช้",
    #         "res_model": 'hr.employee',
    #         "view_mode": "form",
    #         "res_id": employee.id if employee.id else False,
    #         "view_id": self.env["ir.ui.view"].search([('name', '=', 'depa_profile_form')], limit=1).id
    #     }

    def get_action_res_id(self):
        context = self._context
        current_uid = context.get('uid')

        employee = self.sudo().env['hr.employee'].search([
            ('user_id', '=', current_uid)
        ], limit=1)

        action = self.env.ref('depa_profile.depa_profile_window').read()[0]
        action['res_id'] = employee.id if employee.id else False
        # action['view_id'] = self.env["ir.ui.view"].search([('name', '=', 'depa_profile_form')], limit=1).id

        return action