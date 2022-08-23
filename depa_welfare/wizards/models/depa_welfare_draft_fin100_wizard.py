from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date

class depa_welfare_draft_fin100_wizard(models.TransientModel):
    _name = 'depa_welfare_draft_fin100_wizard'

    welfare_id = fields.Many2one(
        'depa_welfare_hr',
    )
    FIN_TYPE = [('erob', 'Expense request of budget')]
    PRIORITY = [('1_normal', 'Normal'),
                ('0_urgent', 'Urgent')]
    priority = fields.Selection(PRIORITY, string='Priority', required=True)

    fin_type = fields.Selection(FIN_TYPE, string='FIN Type', required=True)
    fin_lines = fields.One2many('fw_pfb_fin_system_100_line',
                                'fin_id',
                                copy=True, )
    amount_total = fields.Float()
    depa_amount_total = fields.Float()
    gbdi_amount_total = fields.Float()

    welfare_hr_id = fields.Char()

    projects_and_plan = fields.Many2one('account.analytic.account')
    depa_projects_and_plan = fields.Many2one('account.analytic.account')
    gbdi_projects_and_plan = fields.Many2one('account.analytic.account')

    product_id = fields.Many2one('product.template',
                                 domain=[('fin_ok', '=', True)],
                                 # required=True
                                 )
    depa_product_id = fields.Many2one('product.template',
                                 domain=[('fin_ok', '=', True)],
                                 required=True)
    gbdi_product_id = fields.Many2one('product.template',
                                 domain=[('fin_ok', '=', True)],
                                 required=True)

    description = fields.Char(string='description')
    product_uom_qty = fields.Float(string='Quantity',
                                   # digits=dp.get_precision('Product Unit of Measure'),
                                   # required=True,
                                   default=1.0
                                   )
    product_uom = fields.Many2one('uom.uom',
                                  string='Unit of Measure',
                                  # store=True,
                                  # related='product_id.product_tmpl_id.uom_id',
                                  # required=True
                                  )
    price_unit = fields.Float('Unit Price',
                              # required=True,
                              # digits=dp.get_precision('Product Price'),
                              # store=True,
                              # default=_default_price,
                              # default='product_id.lst_price',
                              )
    depa_product_uom_qty = fields.Float(string='Quantity',
                                   # digits=dp.get_precision('Product Unit of Measure'),
                                   required=True,
                                   default=1.0)
    depa_product_uom = fields.Many2one('uom.uom',
                                  string='Unit of Measure',
                                  store=True,
                                  # related='product_id.product_tmpl_id.uom_id',
                                  required=True)
    depa_price_unit = fields.Float('Unit Price',
                              required=True,
                              # digits=dp.get_precision('Product Price'),
                              store=True,
                              # default=_default_price,
                              # default='product_id.lst_price',
                              )
    gbdi_product_uom_qty = fields.Float(string='Quantity',
                                   # digits=dp.get_precision('Product Unit of Measure'),
                                   required=True,
                                   default=1.0)
    gbdi_product_uom = fields.Many2one('uom.uom',
                                  string='Unit of Measure',
                                  store=True,
                                  # related='product_id.product_tmpl_id.uom_id',
                                  required=True)
    gbdi_price_unit = fields.Float('Unit Price',
                              required=True,
                              # digits=dp.get_precision('Product Price'),
                              store=True,
                              # default=_default_price,
                              # default='product_id.lst_price',
                              )
    standard_price = fields.Float('Standard Price',
                                  store=True,
                                  )
    price_subtotal = fields.Float(compute='_compute_subtotal',
                                  string='Subtotal',
                                  readonly=True,
                                  store=True, )
    depa_price_subtotal = fields.Float(compute='_compute_depa_subtotal',
                                  string='Subtotal',
                                  readonly=True,
                                  store=True, )
    gbdi_price_subtotal = fields.Float(compute='_compute_gbdi_subtotal',
                                  string='Subtotal',
                                  readonly=True,
                                  store=True, )

    @api.depends('price_unit', 'product_uom_qty')
    def _compute_subtotal(self):
        for line in self:
            line['price_subtotal'] = line.product_uom_qty * line.price_unit

    @api.depends('depa_price_unit', 'depa_product_uom_qty')
    def _compute_depa_subtotal(self):
        for line in self:
            line['depa_price_subtotal'] = line.depa_product_uom_qty * line.depa_price_unit

    @api.depends('gbdi_price_unit', 'gbdi_product_uom_qty')
    def _compute_gbdi_subtotal(self):
        for line in self:
            line['gbdi_price_subtotal'] = line.gbdi_product_uom_qty * line.gbdi_price_unit

    def _default_fiscal_year(self):
        fiscal_year_obj = self.env['fw_pfb_fin_system_fiscal_year'].search([
            ('date_start', '<=', date.today()),
            ('date_end', '>=', date.today()),
        ], limit=1)
        if fiscal_year_obj:
            return fiscal_year_obj.id

    is_welfare = fields.Boolean(
        string='Welfare',
        default=True
    )
    fiscal_year = fields.Many2one(
        'fw_pfb_fin_system_fiscal_year',
        compute='_current_fiscal_year',
        store=True
    )
    welfare_round = fields.Integer(
        compute='_depends_welfare_round',
        store=True
    )
    welfare_round_start = fields.Date(
        readonly=True
    )
    welfare_round_end = fields.Date(
        readonly=True
    )

    @api.depends('is_welfare')
    def _current_fiscal_year(self):
        for rec in self:
            fiscal_year_obj = self.env['fw_pfb_fin_system_fiscal_year'].search([
                ('date_start', '<', date.today()),
                ('date_end', '>=', date.today()),
            ], limit=1)
            if fiscal_year_obj:
                rec.fiscal_year = fiscal_year_obj

    @api.depends('fiscal_year')
    def _depends_welfare_round(self):
        for rec in self:
            if rec.fiscal_year:
                welfare_round_line_obj = self.env['depa_welfare_round_lines'].search([
                    ('depa_welfare_round_lines_id.fiscal_year_id', '=', rec.fiscal_year.id),
                    ('welfare_start', '>=', date.today()),
                ], limit=1)
                if welfare_round_line_obj:
                    rec.welfare_round = welfare_round_line_obj.welfare_round
                    rec.welfare_round_start = welfare_round_line_obj.welfare_start
                    rec.welfare_round_end = welfare_round_line_obj.welfare_end

    @api.onchange('is_welfare')
    def _onchange_is_welfare(self):
        if self.is_welfare:
            new_lines = []
            product = self.env['product.template'].search([('active', '=', True)])
            new_lines.append((0, 0, {
                'product_id': 31,
                'price_unit': self.amount_total,
                'product_uom_qty': 1,
                'fin100_state': "draft",
                'product_uom': 1
            }))
            self.fin_lines = new_lines
            # self.fin_lines = [(0, 0, {
            #
            #     'price_unit': self.amount_total,
            # })]
    def action_draft(self):
        # print(self)
        data = {
            "priority": self.priority,
            'fin_type': self.fin_type,
            "fiscal_year": self.fiscal_year.id,
            "welfare_round": self.welfare_round,
            "welfare_round_start": self.welfare_round_start,
            "welfare_round_end": self.welfare_round_end,
            "is_welfare": True,
            "fin_lines": [
                (
                    0,
                    0,
                    {
                        'projects_and_plan': self.depa_projects_and_plan.id,
                        'product_id': self.depa_product_id.id,
                        'product_uom': self.depa_product_uom.id,
                        'price_unit': self.depa_price_unit,
                        'price_subtotal': self.depa_price_subtotal,
                        'is_fin_line_welfare_gbdi': False
                    }
                ),
                (
                    0,
                    0,
                    {
                        'projects_and_plan': self.gbdi_projects_and_plan.id,
                        'product_id': self.gbdi_product_id.id,
                        'product_uom': self.gbdi_product_uom.id,
                        'price_unit': self.gbdi_price_unit,
                        'price_subtotal': self.gbdi_price_subtotal,
                        'is_fin_line_welfare_gbdi': True
                    }
                )
            ]
        }
        self.env['fw_pfb_fin_system_100'].create(data)

        return {
            'type': 'ir.actions.act_window_close'
        }


