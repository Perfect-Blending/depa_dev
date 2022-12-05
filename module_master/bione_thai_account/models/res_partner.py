# -*- coding: utf-8 -*-


from odoo import models, fields, api, _


class BionePartnerContact(models.Model):

    _inherit = 'res.partner'

    #Edit
    name = fields.Char(index=True, track_visibility='onchange')
    vat = fields.Char(track_visibility='onchange')
    street = fields.Char(track_visibility='onchange')
    street2 = fields.Char(track_visibility='onchange')
    zip = fields.Char(change_default=True, track_visibility='onchange')
    city = fields.Char(track_visibility='onchange')
    email = fields.Char(track_visibility='onchange')
    phone = fields.Char(track_visibility='onchange')
    mobile = fields.Char(track_visibility='onchange')

    # Add

    fax = fields.Char(string='Fax', track_visibility='onchange')
    branch_no = fields.Char(string='Branch No', size=5, track_visibility='onchange')

