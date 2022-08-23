# -*- coding: utf-8 -*-

from odoo import models, fields, api
import base64
import os

class depa_signature_setting(models.Model):
    _name = 'depa_signature_setting'

    def _get_email_to_draft(self):
        email = False
        hasSettings = self.env['depa_signature_setting'].search([], limit=1)
        if hasSettings :
          for rec in hasSettings :
            setting = self.env['depa_signature_setting'].browse( rec.id )
            if setting :
                email = setting.email_to_draft
        return email

    def _get_default_url_endpoint(self):
        url = False
        hasSettings = self.env['depa_signature_setting'].search([], limit=1)
        if hasSettings :
          for rec in hasSettings :
            setting = self.env['depa_signature_setting'].browse( rec.id )
            if setting :
                url = setting.url_endpoint
        return url

    def _get_default_cert_path_file(self):
        cert = False
        hasSettings = self.env['depa_signature_setting'].search([], limit=1)
        if hasSettings :
          for rec in hasSettings :
            setting = self.env['depa_signature_setting'].browse( rec.id )
            if setting :
                cert = setting.cert_path_file
        return cert

    def _get_signature_setting_lines(self):
        list = False
        datas = self.env['depa_signature_setting_lines'].search([])
        if datas :
          list = datas
        else :
          list = []

        return list

    def _get_cert_path(self):
        parent_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
        cert_path = os.path.join(parent_path, "wizard", "dSign")
        dir_list = os.listdir(cert_path)
        selection = []
        if dir_list:
            for fname in dir_list:
                if fname.endswith(".p12"):
                    filepath = os.path.join(cert_path, fname)
                    selection.append((filepath, fname))
        return selection

    email_to_draft = fields.Char(
        string="email สำหรับฉบับร่าง",
        required=True,
        default=_get_email_to_draft
    )
    email_credential = fields.Char(
        string="email password",
        required=True
    )
    cert_passphrase = fields.Char(
        string='cert password',
        required = True
    )
    url_endpoint = fields.Char(
        string="API Endpoint",
        default=_get_default_url_endpoint,
        required=True
    )
    cert_path_file = fields.Selection(
        _get_cert_path,
        string="ไฟล์สำหรับเชื่อมต่อ API",
        default=_get_default_cert_path_file,
        required=True
    )
    depa_signature_setting_ids = fields.One2many(
        'depa_signature_setting_lines',
        'depa_signature_setting_id',
        default=_get_signature_setting_lines
    )

    @api.model
    def create(self, vals):
        setting_id = False
        hasSettings = self.env['depa_signature_setting'].search([], limit=1)
        if vals['email_credential']:
            vals['email_credential'] = base64.b64encode(vals['email_credential'].encode('utf-8')).decode('utf-8')
        if vals['cert_passphrase']:
            vals['cert_passphrase'] = base64.b64encode(vals['cert_passphrase'].encode('utf-8')).decode('utf-8')
        if not hasSettings:
            setting_id = super(depa_signature_setting, self).create(vals)
        else:
            for rec in hasSettings:
                setting_id = rec
                setting_id.write(vals)

        if len(setting_id.depa_signature_setting_ids) > 0:
            for line in setting_id.depa_signature_setting_ids:
                if line.destroy:
                    line.unlink()

        return setting_id

    @api.multi
    def apply(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }


class depa_signature_setting_lines(models.Model):
    _name = 'depa_signature_setting_lines'

    depa_signature_setting_id = fields.Many2one(
        'depa_signature_setting'
    )
    employee_id = fields.Many2one(
        'hr.employee',
        required=True
    )
    cad_password = fields.Text(
        string='CAD',
        required = True
    )
    disable = fields.Boolean(
        string='Disable',
        default=False
    )
    destroy = fields.Boolean(
        string='Delete',
        default=False
    )
    otp_default = fields.Boolean(
        string='default OTP',
        default=False
    )
    active = fields.Boolean(
        string='Active',
        default=True
    )