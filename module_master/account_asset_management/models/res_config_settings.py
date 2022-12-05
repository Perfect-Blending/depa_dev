# Copyright (c) 2014 ACSONE SA/NV (http://acsone.eu).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class Config(models.TransientModel):
    _inherit = 'res.config.settings'

    module_account_asset_management = fields.Boolean(
        string='Assets management (OCA)',
        help="""This allows you to manage the assets owned by a company
                or a person. It keeps track of the depreciation occurred
                on those assets, and creates account move for those
                depreciation lines.
                This installs the module account_asset_management.""")

    asset_journal_id = fields.Many2one('account.journal', string='Asset Journal', index=True, required=True)

    @api.model
    def get_values(self):
        res = super(Config, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            asset_journal_id=int(
                params.get_param('account_asset_management.asset_journal_id', default=False)) or False,
        )
        return res

    @api.multi
    def set_values(self):
        super(Config, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param("account_asset_management.asset_journal_id", self.asset_journal_id.id or False)
