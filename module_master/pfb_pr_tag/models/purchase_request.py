from odoo import models, fields, api, _


class PurchaseRequestTag(models.Model):
    _name = "purchase.request.setting.tag"
    _description = "Purchase Request tag"

    name = fields.Char(string="Document Tag", required=True, copy=False)
    color = fields.Integer(string='Color Index')
    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]


class PurchaseRequestNTPInherit(models.Model):
    _inherit = 'purchase.request'

    tag_ids = fields.Many2many('purchase.request.setting.tag', string="tag", track_visibility='onchange')
    number_pr = fields.Char(string="เลขที่ PR")

# class PurchaseRequestLineNTPInherit(models.Model):
#     _inherit = 'purchase.request.line'
#
#     depot = fields.Many2one('purchase.request.depot', string='Depot')
#     customs_pr = fields.Many2one('res.partner', string='Customs', domain="[('customer_rank','>', 0)]")
#     location_pr = fields.Many2one('res.partner', string='Location')
#     remark = fields.Char(string='Remark', )
