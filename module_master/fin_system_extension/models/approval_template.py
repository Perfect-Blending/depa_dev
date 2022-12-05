# -*- coding: utf-8 -*-
# ProThai Technology Co., Ltd.

from odoo import api, fields, models, _


class fw_pfb_flow_template(models.Model):
    _inherit = 'fw_pfb_flow_template'

    @api.model
    def create(self, vals):
        res = super(fw_pfb_flow_template, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        res = super(fw_pfb_flow_template, self).write(vals)
        return res


class fw_pfb_flow_template_approve(models.Model):
    _inherit = 'fw_pfb_flow_template_approve'

    approval_type = fields.Selection([
        #('optional', 'Approves, but the approval is optional'),
        ('mandatory', 'Is required to approve'),
        ('comment', 'Comments only'),
        ], 'Approval Type',
        default='mandatory', required=True)
    approve_step = fields.Integer(string='Step', default=0, required=True)
    trigger = fields.Integer(string="trigger")

    @api.model
    def create(self, vals):
        res = super(fw_pfb_flow_template_approve, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        res = super(fw_pfb_flow_template_approve, self).write(vals)
        return res
