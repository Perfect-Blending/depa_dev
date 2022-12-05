# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class CurrencyRate(models.Model):
    _inherit = "res.currency.rate"

    # overide currency_id to set required=True
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True, required=True)
    # for search
    currency_active = fields.Boolean(related='currency_id.active', string='Active', store=True, readonly=True)
    rate = fields.Float(string ="Buy Rate",digits=(12, 6), help='The rate of the currency to the currency of rate 1')
    sell_rate = fields.Float(string ="Sell Rate ",digits=(12, 6), help='The rate of the currency to the currency of rate 1')


class Currency(models.Model):
    _inherit = "res.currency"

    @api.multi
    def _compute_current_rate_sell(self):
        date = self._context.get('date') or fields.Date.today()
        company_id = self._context.get('company_id') or self.env['res.users']._get_company().id
        # the subquery selects the last rate before 'date' for the given currency/company
        query = """SELECT c.id, (SELECT r.sell_rate FROM res_currency_rate r
                                  WHERE r.currency_id = c.id AND r.name <= %s
                                    AND (r.company_id IS NULL OR r.company_id = %s)
                               ORDER BY r.company_id, r.name DESC
                                  LIMIT 1) AS rate
                   FROM res_currency c
                   WHERE c.id IN %s"""
        self._cr.execute(query, (date, company_id, tuple(self.ids)))
        currency_rates = dict(self._cr.fetchall())
        for currency in self:
            currency.sell_rate = currency_rates.get(currency.id) or 1.0

    rate = fields.Float(compute='_compute_current_rate', string='Current Buy Rate', digits=(12, 6),
                        help='The rate of the currency to the currency of rate 1.')
    sell_rate = fields.Float(compute='_compute_current_rate_sell', string='Current Sell Rate', digits=(12, 6),
                        help='The rate of the currency to the currency of rate 1.')


    @api.model
    def _get_conversion_rate(self, from_currency, to_currency, sell=True):
        if self._context.get('rate'):
            if sell:
                if self._context.get('late_rate'):
                    res= self._context.get('late_rate')/self._context.get('rate')
                else:
                    res = to_currency.sell_rate/self._context.get('rate')
            else:
                if self._context.get('late_rate'):
                    res= self._context.get('late_rate')/self._context.get('rate')
                else:
                    res = to_currency.rate/self._context.get('rate')
        if not self._context.get('rate'):
            if sell:
                res = self._get_conversion_sell_rate(from_currency, to_currency)
            else:
                res = self._get_conversion_buy_rate(from_currency, to_currency)
        return res

    @api.model
    def _get_conversion_sell_rate(self, from_currency, to_currency):
        from_currency = from_currency.with_env(self.env)
        to_currency = to_currency.with_env(self.env)
        return to_currency.sell_rate / from_currency.sell_rate

    @api.model
    def _get_conversion_buy_rate(self, from_currency, to_currency):
        from_currency = from_currency.with_env(self.env)
        to_currency = to_currency.with_env(self.env)
        return to_currency.rate / from_currency.rate

    @api.multi
    def compute(self, from_amount, to_currency, round=True):
        """ Convert `from_amount` from currency `self` to `to_currency`. """
        self, to_currency = self or to_currency, to_currency or self
        assert self, "compute from unknown currency"
        assert to_currency, "compute to unknown currency"
        # apply conversion rate
        if self == to_currency:
            to_amount = from_amount
        else:
            if self._context.get('type') in ['out_invoice','inbound','out_refund','out_charge','out_deposit','out','sale','PR']:
                to_amount = from_amount * self._get_conversion_rate(self, to_currency)
            else:
                to_amount = from_amount * self._get_conversion_rate(self, to_currency,sell =False)
        # apply rounding
        return to_amount
        #return to_currency.round(to_amount) if round else to_amount

    #@api.model
    #def _get_conversion_rate(self, from_currency, to_currency,_type=None):
        #currency_rate_config = None
        #context = self._context.get("params")
        #p_id = context and self._context.get("params").get("id")
        #p_model = context and self._context.get("params").get("model")

        #type_currency_rate = self._context.get("type")
        #if p_id and p_model:
            #currency_rate_config = self.env[p_model].browse(p_id)
            #currency_rate_config = currency_rate_config.currency_rate

        #if type_currency_rate in ('out_invoice','out_refund','out_charge','out_deposit','inbound'): #Sell
            #from_currency = currency_rate_config or from_currency.with_env(self.env).sell_rate
            #to_currency = to_currency.with_env(self.env)
            #to_currency = to_currency.sell_rate
        #else:
            #from_currency = currency_rate_config or from_currency.with_env(self.env).rate
            #to_currency = to_currency.with_env(self.env)
            #to_currency = to_currency.rate
        #return from_currency / to_currency # reverse for account thai


    #def _select_companies_rates(self):
        #res= super(Currency,self)._select_companies_rates()
        #return """
            #SELECT
                #r.currency_id,
                #COALESCE(r.company_id, c.id) as company_id,
                #r.rate,r.sell_rate,
                #r.name AS date_start,
                #(SELECT name FROM res_currency_rate r2
                 #WHERE r2.name > r.name AND
                       #r2.currency_id = r.currency_id AND
                       #(r2.company_id is null or r2.company_id = c.id)
                 #ORDER BY r2.name ASC
                 #LIMIT 1) AS date_end
            #FROM res_currency_rate r
            #JOIN res_company c ON (r.company_id is null or r.company_id = c.id)
        #"""

