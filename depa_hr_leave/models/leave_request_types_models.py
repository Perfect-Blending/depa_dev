# -*- coding: utf-8 -*-

from odoo import models, fields, api

class leave_request_types(models.Model):
    _name = "leave_request_types"

    name = fields.Char(
        string="ประเภทการลา"
    )
    en_name = fields.Char(
        string="ประเภทการลา (ภาษาอังกฤษ)"
    )
    is_primary_approval = fields.Boolean(
        string="ผู้อนุมัติขั้นต้น",
        default=True
    )
    request_type_approval_id = fields.Many2one(
        "hr.employee",
        string="เลือกผู้อนุมัติการลา"
    )
