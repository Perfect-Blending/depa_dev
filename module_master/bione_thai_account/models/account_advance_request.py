# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError


class AccountAdvanceRequest(models.Model):
    _name = "account.advance.request"
    _description = 'Advance Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "id desc,name desc"

    _CONTROL_STATE = {"draft": [("readonly", False)]}
    _REQUIRED = {'required': True, 'readonly': True, 'states': {'draft': [('readonly', False)]}}
    _OPTIONAL = {'required': False, 'readonly': True, 'states': {'draft': [('readonly', False)]}}

    @api.one
    @api.depends('lines', 'company_id', 'date')
    def _compute_amount(self):
        self.amount_total = sum(line.amount for line in self.lines)

    def get_count(self):
        for obj in self:
            advance_count = 0
            advance = obj.env['account.advance'].search([('advance_request_id', '=', obj.id)])
            for aucs in advance:
                advance_count += 1
            obj.advance_count = advance_count

    @api.returns('self')
    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    @api.returns('self')
    def _default_department(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1).department_id

    name = fields.Char('Number', copy=False, default=lambda x: _('New'), index=True, readonly=True)
    date = fields.Date('Date', copy=False, index=True, default=fields.Date.context_today, **_REQUIRED,)
    date_due = fields.Date('Due Date', copy=False, index=True, default=fields.Date.context_today, **_REQUIRED)

    notes = fields.Text(string='Notes', **_OPTIONAL)
    employee_id = fields.Many2one('hr.employee', 'Employee', index=True, **_REQUIRED, default=_default_employee)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id, index=True,
                                 **_REQUIRED)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Waiting For Approved'),
        ('approved', 'Approved'),
        ('cancel', 'Cancelled')], string='State',
        copy=False, default='draft', track_visibility='onchange', index=True)
    #    currency_id = fields.Many2one('res.currency', string='Currency',
    #        required=True, readonly=True, states={'draft': [('readonly', False)]},
    #        track_visibility='always')
    lines = fields.One2many('account.advance.request.line', 'advance_request_id', string='Lines')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_compute_amount')
    advance_id = fields.One2many('account.advance', 'ref', string='Advance')
    currency_id = fields.Many2one('res.currency', string='Currency', index=True,
                                  required=True, readonly=True, states={'draft': [('readonly', False)]},
                                  default=lambda self: self.env.user.company_id.currency_id, track_visibility='always')
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency",
                                          readonly=True, index=True)
    currency_rate = fields.Float("Exchange Rate", readonly=True, states={'draft': [('readonly', False)]},
                                 digits=(12, 6))
    currency_rate_date = fields.Date("Exchange Rate Date", readonly=True, states={'draft': [('readonly', False)]})
    advance_ids = fields.One2many('account.advance', 'advance_request_id', string='Advance')
    advance_count = fields.Integer("Count Advance", compute="get_count", default=0)

    title_id_advance = fields.Many2one('advance.requisition.title','วัตถุประสงค์',required=False)
    description = fields.Text('รายละเอียด (ถ้ามี)', copy=False, **_OPTIONAL)
    user_id = fields.Many2one('res.users', string='Created by', required=False, default=lambda self: self.env.user)
    # Contract information
    memo_no = fields.Char()
    memo_date = fields.Date()
    contract_no_advance = fields.Char('Contract no')
    contract_amount = fields.Float('Contract Amount')
    contract_start = fields.Date('Contract Start')
    contract_end = fields.Date('Contract End')
    contract_details = fields.Text('Contract Details')
    due_date = fields.Datetime()
    # method_of_recruitment = fields.Many2one('budget_system.method_of_recruitment')
    warranty_end = fields.Date()
    delivery_address = fields.Text()
    delivery_date = fields.Date()
    # Budget details
    # budget_source = fields.Many2one('budget.fund_management', string='งบประมาณ',domain=[('state', '=','success')])
    department = fields.Many2one('hr.department', string='Department', **_REQUIRED, default=_default_department,)

    @api.onchange('currency_id', 'date')
    def onchange_currency_id(self):
        currency_id = self.currency_id.id
        currency = self.env["res.currency"].browse(currency_id).with_context(date=self.date)
        for line in self.lines:
            line.currency_id = self.currency_id.id
        if currency:
            self.currency_rate = currency.rate
            self.currency_rate_date = currency.date

    @api.multi
    def action_draft(self):
        self.state = 'draft'
        return True

    @api.multi
    def action_cancel(self):
        if self.state not in 'draft':
            if self.state in 'approved':
                advance = self.env['account.advance'].search([('ref', '=', self.name)])
                if advance:
                    if advance.state == 'draft':
                        for obj in advance:
                            advance.update({'state': 'cancel'})
                            # Delete non-manual tax lines
                            # self._cr.execute("DELETE FROM account_advance_line WHERE advance_id=%s ", (obj.id,))
                            # self._cr.execute("DELETE FROM account_advance WHERE id=%s ", (obj.id,))
                    elif advance.state == 'confirmed':
                        raise UserError(_('Not allow to cancel this document (%s)' % (self.name_get()[0][1])))
                    elif advance.state == 'done':
                        raise UserError(_('Not allow to cancel this document (%s)' % (self.name_get()[0][1])))
        self.update({'state': 'cancel'})
        return True

    @api.multi
    def button_get_advance(self):
        return {
            'name': _('Advance'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.advance',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.advance_ids.ids)],
        }

        return True

    @api.multi
    def button_validate(self):
        self.update({'state': 'approved'})
        self._create_account_advance()
        return True

    @api.multi
    def button_submit(self):
        name = self.env['ir.sequence'].with_context(ir_sequence_date=self.date).next_by_code('account.advance.request')
        self.update({'state': 'submit', 'name': name})
        return True

    # @api.model
    # def create(self, vals):
    #     vals['name'] = self.env['ir.sequence'].with_context(
    #         ir_sequence_date=vals.get('date')).next_by_code('account.advance.request')
    #     return super(AccountAdvanceRequest, self).create(vals)

    @api.multi
    def unlink(self):
        check = [(obj) for obj in self if obj.state not in ('draft') or (obj.name and obj.name != '/')]
        if check:
            raise UserError(_('You cannot delete. You must cancel only.'))
        else:
            return super(AccountAdvanceRequest, self).unlink()

    @api.multi
    def _create_account_advance(self):
        for obj in self:
            vals = {
                'name': '',#self.env['ir.sequence'].next_by_code('account.advance'),
                'date': self.date,
                'date_due': self.date_due,
                'description': self.description,
                'note': self.notes,
                'employee_id': self.employee_id.id,
                'company_id': self.company_id.id,
                'currency_rate': self.currency_rate,
                'currency_rate_date': self.currency_rate_date,
                'currency_id': self.currency_id.id,
                'amount_total': self.amount_total,
                'ref': self.name,
                'advance_request_id': self.id,
                'lines': [],
                'title_id_advance': self.title_id_advance.id,
            }
            for line in self.lines:
                line_vals = {
                    'name': line.name,
                    'amount': line.amount,
                    'product_id': line.product_id.id,
                    'analytic_account_id': line.analytic_account_id.id,
                }
                vals['lines'].append((0, 0, line_vals))
            advance = self.env['account.advance'].create(vals)

            # vals = {
            #     'title_id': self.title_id.id,
            #     'department': self.department.id,
            #     'employee_id': self.employee_id.id,
            #     'budget_source': self.budget_source.id,

            # }

            # advance.write({vals})

        return advance


class AccountAdvanceRequestLine(models.Model):
    _name = "account.advance.request.line"

    advance_request_id = fields.Many2one('account.advance.request', 'Advance Request', required=True, index=True)
    product_id = fields.Many2one("product.product", "Product", required=True, index=True)
    name = fields.Char('Description', required=True)
    amount = fields.Monetary(string="Amount", required=True)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', index=True)
    currency_id = fields.Many2one('res.currency', string='Currency', related='advance_request_id.currency_id',
                                  required=False, index=True)

class AdvanceRequisitionTitle(models.Model):
    _name = "advance.requisition.title"

    name = fields.Char('Description', copy=False)
