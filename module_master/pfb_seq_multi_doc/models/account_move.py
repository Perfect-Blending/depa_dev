from odoo import models, fields, api, _


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    doc_seq_number2 = fields.Char(string="Number")

    doc_seq_number = fields.Char(string="Number", index=True, copy=False, default=lambda self: _(''))

    doc_seq_type = fields.Many2one('ir.sequence', string='Type', domain=[('account_active', '=', True)], copy=False)

    @api.model
    def create(self, vals):
        if not self.doc_seq_number or vals.get("doc_seq_type", False):
            if vals.get("doc_seq_type", self.doc_seq_type.id):
                seq_i = self.env['ir.sequence'].browse(vals.get("doc_seq_type", self.doc_seq_type.id))
                if vals.get('date', self.date):
                    seq_i = self.env['ir.sequence'].with_context(ir_sequence_date=vals.get('date', self.date)) \
                        .browse(vals.get("doc_seq_type", self.doc_seq_type.id))
                vals['doc_seq_number'] = seq_i.next_by_id()
                vals['doc_seq_number2'] = vals['doc_seq_number']
        ret = super(AccountMoveInherit, self).create(vals)
        return ret

    @api.multi
    def write(self, vals):
        if not self.doc_seq_number or vals.get("doc_seq_type", False):
            if vals.get("doc_seq_type", self.doc_seq_type.id):
                seq_i = self.env['ir.sequence'].browse(vals.get("doc_seq_type", self.doc_seq_type.id))
                if vals.get('date', self.date):
                    seq_i = self.env['ir.sequence'].with_context(ir_sequence_date=vals.get('date', self.date))\
                        .browse(vals.get("doc_seq_type", self.doc_seq_type.id))
                vals['doc_seq_number'] = seq_i.next_by_id()
                vals['doc_seq_number2'] = vals['doc_seq_number']
        ret = super(AccountMoveInherit, self).write(vals)


