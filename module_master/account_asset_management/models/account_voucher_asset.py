# Copyright 2009-2018 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models, tools , _
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp
_logger = logging.getLogger(__name__)

class AccountGenerateMove(models.Model):
    _inherit = 'account.move'
    voucher_asset_generate = fields.Char(string='Asset Generate No.',readonly=True)
    asset_profile_id = fields.Many2one(
        comodel_name='account.asset.profile',
        string='Asset Profile')
class account_voucher_asset(models.Model):

    _name = 'account.voucher.asset'
    name = fields.Char(string='Asset Generate No.',readonly=True)#fields.Many2one(comodel_name='account.account', string='Account')
    date = fields.Date(string='Date')
    asset_profile_id = fields.Many2one(
        comodel_name='account.asset.profile',
        string='Asset Profile')
    # ref = fields.Char(string='Reference')
    # journal_id = fields.Many2one('account.journal', string='Journal')
    total = fields.Float(string='Total', digits=dp.get_precision('account'))
    voucher_asset_ids = fields.One2many('account.voucher.asset.item', 'voucher_asset_id',string='Asset Item')
    voucher_move_ids = fields.One2many('account.voucher.asset.move', 'voucher_move_id', string='Journal Entries')
    # state = fields.Char(string='Status')
    # asset_id = fields.Many2one(comodel_name='account.asset', string='Asset')

    def action_asset_generate_no_action(self):
        cr = self.env.cr
        params = self.env['ir.config_parameter'].sudo()
        asset_journal_id = int(
            params.get_param('account_asset_management.asset_journal_id', default=False)) or False,

        if asset_journal_id == False:
            raise UserError(_("Please set Asset Journal"))
        sql = (''' SELECT    
                              l.asset_id
                              ,l.move_id
                              ,l.journal_id
                              ,m.ref
                              ,m.date
                              ,m.state
                              ,p.id as profile_id
                              ,p.name as profile_name
                      FROM account_move_line l
                      LEFT JOIN account_move m ON m.id = l.move_id
                      LEFT JOIN account_asset a ON a.id = l.asset_id
                      LEFT JOIN account_asset_profile p ON p.id = a.profile_id
                      WHERE m.journal_id = %s AND m.voucher_asset_generate IS NULL
                      GROUP BY
                          m.date
                          ,l.asset_id
                          ,l.move_id
                          ,l.journal_id
                          ,m.ref
                          ,m.date
                          ,m.state
                          ,p.id 
               ''')
        cr.execute(sql,asset_journal_id)
        result = cr.dictfetchall()

        date_all = []
        for row in result:
            date = row.get('date', False)
            # print(move_id)
            # move_id_update = []
            if date not in date_all:
                date_all.append(date)
                # print(date)
                profile_id_all = []
                for row2 in result:
                    profile_id = row2.get('profile_id', False)

                    if date == row2.get('date', False):
                        if profile_id not in profile_id_all:
                            sequence = self.env['ir.sequence'].with_context(ir_sequence_date=date).next_by_code('account.voucher.asset')
                            # print(row2.get('profile_id', False))
                            profile_id_all.append(profile_id)
                            # print(profile_id)
                            move_id_update = []

                            for row3 in result:
                                move_id = row3.get('move_id', False)
                                if date == row3.get('date', False):
                                    if row3.get('profile_id', False) == profile_id:
                                        if move_id not in move_id_update:
                                            move_id_update.append(move_id)
                                            # print(move_id)


                            if move_id_update:
                                cr.execute('UPDATE account_move SET '
                                           'voucher_asset_generate=%s , asset_profile_id = %s'
                                           ' WHERE id IN %s', (sequence,profile_id, tuple(move_id_update),))


        self.action_asset_item_voucher_action()

        return {
            'name': _('Item Voucher Asset'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.voucher.asset',
            'view_id': False,
            # 'domain': [('id', 'in', asset_move_item_ids)],
            'type': 'ir.actions.act_window',
        }

    def action_asset_item_voucher_action(self):
        cr = self.env.cr

        params = self.env['ir.config_parameter'].sudo()
        asset_journal_id = int(
            params.get_param('account_asset_management.asset_journal_id', default=False)) or False,
        self.search([]).unlink()

        sql = (''' SELECT
                          m.date,
                          m.asset_profile_id,
                          m.voucher_asset_generate as name,
                          m.amount,
                         COALESCE(SUM(l.debit),0) AS debit, 
                         COALESCE(SUM(l.credit),0) AS credit, 
                         COALESCE(SUM(l.debit - l.credit),0) AS balance,
                          l.account_id,
                          l.asset_id
                FROM  account_move m
                LEFT JOIN account_move_line l ON (l.move_id=m.id)
                WHERE m.journal_id = %s
                GROUP BY 
                	 m.date,
                     m.asset_profile_id,
                     m.voucher_asset_generate,
                     m.amount,
                     l.account_id,
                     l.asset_id
                ORDER BY m.date DESC
                ''')

        cr.execute(sql,asset_journal_id)
        result = cr.dictfetchall()
        name_vc = []

        for row in result:
            # # print(asset_id)
            date = row.get('date', False)
            asset_profile_id = row.get('asset_profile_id', False)
            name = row.get('name', False)

            record_move = []
            asset_ids = []

            if name not in name_vc:
                name_vc.append(name)
                account_ids = []
                asset_ids_item = []
                total = 0

                for row2 in result:

                    if name == row2.get('name', False):
                        total += row2.get('debit', False)
                        asset_profile_id = row2.get('asset_profile_id', False)
                        account_id = row2.get('account_id', False)


                        if account_id not in account_ids:
                            account_ids.append(account_id)
                            debit = 0
                            credit = 0
                            for row3 in result:
                                if name == row3.get('name',False):
                                    if account_id == row3.get('account_id',False):
                                        debit += row3.get('debit', False)
                                        credit += row3.get('credit', False)
                                        # print(row3.get('debit', False))

                            row_move = {
                                'name': account_id,
                                'debit': debit,
                                'credit': credit,
                                'asset_profile_id': asset_profile_id,
                            }
                            record_move.append((0, 0, row_move))

                        asset_id = row2.get('asset_id', False)
                        if asset_id not in asset_ids_item:
                            asset_ids_item.append(asset_id)

                            asset_item = {
                                'name': asset_id,
                            }
                            asset_ids.append((0, 0, asset_item))

                val = {
                    'asset_profile_id': asset_profile_id,
                    'name': name,
                    'date': date,
                    'total': total,
                    'voucher_asset_ids': asset_ids,
                    'voucher_move_ids': record_move,
                }
                # print(val)
                record = self.create(val)

        return {
            'name': _('Item Voucher Asset'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.voucher.asset',
            'view_id': False,
            # 'domain': [('id', 'in', asset_move_item_ids)],
            'type': 'ir.actions.act_window',
        }

#บอกว่ามาจากค่าเสื่อมตัวไหนบ้าง
class Accoun_item_voucher(models.TransientModel):
    _name = 'account.voucher.asset.item'
    name = fields.Many2one(comodel_name='account.asset', string='Asset')
    voucher_asset_id = fields.Many2one('account.voucher.asset', string='Voucher')

#รายการที่รวมค่าเสื่อมไว้
class AccountMoveLine_group_voucher(models.TransientModel):
    _name = 'account.voucher.asset.move'
    name = fields.Many2one(comodel_name='account.account',string='Account')
    debit = fields.Float(string='Debit', digits=dp.get_precision('account'))
    credit = fields.Float(string='Credit', digits=dp.get_precision('account'))
    voucher_move_id = fields.Many2one('account.voucher.asset', string='Voucher')
    asset_profile_id = fields.Many2one(comodel_name='account.asset.profile',string='Asset Profile')

