# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.http import request
from requests import get

class depa_device(models.Model):
    _name = 'depa_device'

    name = fields.Char(
        string="ชื่ออุปกรณ์",
        required=True
    )

    device_line_ids = fields.One2many(
        "depa_device_lines",
        "device_id",
        string="รหัสอุปกรณ์"
    )
    
    def _check_device_using(self, serial, employee_id):
        serial_id = self.env['hr_employee_hold'].search([
            ('product_code', '=', serial),
            ('active', '=', True),
            ('employee_hold_id', '!=', employee_id)
        ], limit=1)
        if serial_id:
            return serial_id['id']
        return False

    def _change_device_status(self, hold_id):
        device_holding = self.env['hr_employee_hold'].browse(hold_id)
        if device_holding:
            device_holding.update({
                'active': False
            })

    def _add_device_to_employee(self, asset_name, serial, employee_id):
        device_holding = request.env['hr_employee_hold']
        holding_data = {
            'employee_hold_id': employee_id,
            'assets_name': asset_name,
            'product_code': serial,
            'active': True
        }
        device_holding_id = device_holding.create(holding_data)
        return device_holding_id

    @api.model
    def create(self, vals):
        asset_name = vals['name']
        for val in vals['device_line_ids']:
            serial = val[2]['serial']
            employee = val[2]['employee_id']
            if employee:
                self._add_device_to_employee(asset_name=asset_name, serial=serial, employee_id=employee)
        return super(depa_device, self).create(vals)

    @api.multi
    def write(self, vals):
        asset_name = vals.get("name", self.name)
        for val in vals['device_line_ids']:
            depa_device_lines_id = val[1]
            if not val[2]:
                continue
            serial = val[2].get("serial")
            employee = val[2].get("employee_id")
            if serial is None:
                serial_data = self.env["depa_device_lines"].search([
                    ('id', '=', depa_device_lines_id)
                ], limit=1)
                if serial_data:
                    serial = serial_data['serial']
            hold_id = self._check_device_using(serial=serial, employee_id=employee)
            if hold_id:
                self._change_device_status(hold_id=hold_id)
            if employee:
                self._add_device_to_employee(asset_name=asset_name, serial=serial, employee_id=employee)
        return super(depa_device, self).write(vals)

    @api.multi
    def unlink(self):
        for rec in self:
            for line in rec.device_line_ids:
                device_holding = self.env["hr_employee_hold"].search([
                    ('product_code', '=', line.serial),
                    ('active', '=', True)
                ], limit=1)
                if device_holding:
                    device_holding.update({
                        'active': False
                    })

        return super(depa_device, self).unlink()

class depa_device_lines(models.Model):
    _name = 'depa_device_lines'

    serial = fields.Char(
        string="รหัสอุปกรณ์",
        required=True
    )

    device_id = fields.Many2one(
        "depa_device",
        string="ชื่ออุปกรณ์",
    )
    
    employee_id = fields.Many2one(
        "hr.employee",
    )

    @api.multi
    def unlink(self):
        for rec in self:
            device_holding = self.env["hr_employee_hold"].search([
                ('product_code', '=', rec.serial),
                ('active', '=', True)
            ], limit=1)
            if device_holding:
                device_holding.update({
                    'active': False
                })

        return super(depa_device_lines, self).unlink()