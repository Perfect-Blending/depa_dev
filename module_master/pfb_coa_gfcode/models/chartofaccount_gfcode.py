from odoo import api, fields, models
from odoo.osv import expression

class AccountAccount(models.Model):
    _inherit = 'account.account'

    gf_code = fields.Char(string='GF Code', required=False)
    gf_id = fields.Many2one(comodel_name='gf.code')

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        if self._context.get('gf_code_mode') == 'gf_code':
            args = args or []

            # จัดกลุ่มไม่ให้มีค่าซ้ำขึ้นมา
            sql = ''' SELECT DISTINCT gf_code FROM account_account WHERE gf_code != '' '''
            self._cr.execute(sql)
            query_res = self._cr.dictfetchall()
            account_ids_groups = []
            for res in query_res:
                account_id = self.env['account.account'].search([('gf_code', '=', res['gf_code'])],limit=1)
                if account_id not in account_ids_groups:
                    account_ids_groups.append(account_id.id)

            domain = [('id','in',account_ids_groups)]
            #END จัดกลุ่มไม่ให้มีค่าซ้ำขึ้นมา

            if name:
                domain = ['|', ('gf_code', '=ilike', name.split(' ')[0] + '%'), ('name', operator, name)]
                if operator in expression.NEGATIVE_TERM_OPERATORS:
                    domain = ['&', '!'] + domain[1:]

            account_ids = self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
            return self.browse(account_ids).name_get()
        else:
            return super(AccountAccount, self)._name_search(name, args=None, operator='ilike', limit=100, name_get_uid=None)

    @api.multi
    def name_get(self):
        if self._context.get('gf_code_mode') == 'gf_code':
            result = []
            for account in self:
                name = account.gf_code #+ ' ' + account.name
                result.append((account.id, name))
            return result
        else:
            return super(AccountAccount, self).name_get()

class AccountGFCode(models.Model):
    _name = 'gf.code'

    name = fields.Char(required=True)
    gf_code_id = fields.Many2one(
        comodel_name='account.account', string='GF Code', copy=False, required=True)
    gf_code_text = fields.Char(string='Name', related='gf_code_id.gf_code',store=True, readonly=False)

    _sql_constraints = [('gf_code_text_uniq', 'unique (gf_code_text)', "GF Code already exists !")]


    def _update_related(self,vals,gf_code):

        if vals.get('gf_code_text'):
            account_ids = self.env['account.account'].search([('gf_code', '=', vals.get('gf_code_text'))])
            # print('account_ids',account_ids)
            account_ids.write({'gf_id': gf_code.id})
        return True
    @api.model
    def create(self, vals):
        id = super(AccountGFCode, self).create(vals)
        self._update_related(vals,id)
        return id

    @api.multi
    def write(self, vals):
        id = super(AccountGFCode, self).write(vals)
        self._update_related(vals, id)
        return id




