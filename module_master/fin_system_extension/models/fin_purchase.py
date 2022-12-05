# -*- coding: utf-8 -*-
# ProThai Technology Co., Ltd.


from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from random import randrange


class fw_pfb_FS_purchase(models.Model):
    _inherit = 'fw_pfb_fin_system_purchase'

    purchase_order_ids = fields.One2many('purchase.order', 'fin_purchase_id', string="Purchase Orders")
    purchase_order_count = fields.Integer('Purchase Orders Count', compute='_get_purchase_order_datas', store=True)

    trigger = fields.Integer(string="trigger")

    next_approval_id = fields.Many2one('fw_pfb_fin_system_purchase_approver', string='Next Approval', compute='_compute_next_approval', store=True)
    next_approval_ids = fields.Many2many('fw_pfb_fin_system_purchase_approver', string='Next Approval IDS',
        relation="fin_purchase_approval_approver_rel", column1='fin_purchase_id', column2='approval_id', compute='_compute_next_approval', store=True)
    next_approval_user_ids = fields.Many2many('res.users', string='Next Approval Users',
        relation="fin_purchase_approval_res_users_rel", column1='fin_purchase_id', column2='user_id', compute='_compute_next_approval', store=True)
    can_approve = fields.Boolean('Can Approve', compute='_compute_can_approve')

    next_comment_ids = fields.Many2many('fw_pfb_fin_system_purchase_approver', string='Next Comment',
        relation="fin_system_purchase_to_approver_rel", column1='fin_purchase_id', column2='approval_id', compute='_compute_next_comment', store=True)
    next_comment_user_ids = fields.Many2many('res.users', string='Next Comment Users',
        relation="fin_purchase_comment_res_users_rel", column1='fin_purchase_id', column2='user_id', compute='_compute_next_comment', store=True)
    can_comment = fields.Boolean('Can Comment', compute='_compute_can_comment')

    show_button_make_approval = fields.Boolean('Show Make Approval', compute='_compute_hide_button_make_approval')
    hide_button_make_approval = fields.Boolean('Hide Make Approval', compute='_compute_hide_button_make_approval')
    can_complete = fields.Boolean('Can Complete', compute='_compute_can_complete')

    def _compute_can_complete(self):
        print("FIN_PURCHASE._compute_can_complete",self)
        for fin_purchase in self:
            fin_purchase.can_complete = False
            last_approval = fin_purchase.approver and fin_purchase.approver.sorted(lambda app: app.position_index)[-1] or False
            if last_approval:
                if self.env.user.id in last_approval.employee_user_id.ids:
                    fin_purchase.can_complete = True
                else:
                    fin_purchase.can_complete = False
                # force admin can complete
                if self.env.user.id == 1:
                    fin_purchase.can_complete = True
            if fin_purchase.is_fin_lock:
                fin_purchase.can_complete = False

    #@api.depends('purchase_order_ids', 'purchase_order_ids.state', 'next_approval_id', 'next_approval_user_ids', 'state', 'trigger')
    def _compute_hide_button_make_approval(self):
        print("FIN_PURCHASE._compute_hide_button_make_approval",self)
        # po-states --> ['draft','sent','to approve','purchase', 'done', 'cancel']
        for fin_purchase in self:
            show = True
            hide = False
            if fin_purchase.state == 'ManagerOfStock':
                if fin_purchase.purchase_order_ids:
                    if all(po_state=='cancel' for po_state in fin_purchase.purchase_order_ids.mapped('state')):
                        show = False
                        hide = True
                    elif all(po_state=='done' for po_state in fin_purchase.purchase_order_ids.mapped('state')):
                        show = True
                        hide = False
                    elif all(po_state=='purchase' for po_state in fin_purchase.purchase_order_ids.mapped('state')):
                        show = True
                        hide = False
                    else:
                        for po_state in fin_purchase.purchase_order_ids.mapped('state'):
                            if po_state in ['draft','sent','to approve']:
                                show = False
                                hide = True
                                break
                else:
                    show = False
                    hide = True
            fin_purchase.show_button_make_approval = show
            fin_purchase.hide_button_make_approval = hide

    @api.multi
    @api.depends('state', 'approver',
        'approver.employee_id', 'approver.employee_id.user_id', 'approver.employee_user_id',
        'approver.action_date', 'approver.state', 'trigger')
    def _compute_next_approval(self):
        print("FIN_PURCHASE._compute_next_approval",self)
        for fin_purchase in self:
            if fin_purchase.state == 'reject':
                fin_purchase.next_approval_id = False
                return True
            latest_approval_ids = fin_purchase.approver.filtered(lambda app: app.approval_type=='mandatory' and app.state=='approve' and app.approve_active==True)
            latest_approval = latest_approval_ids and latest_approval_ids[-1]
            if latest_approval:
                approval_ids_ready = fin_purchase.approver\
                    .filtered(lambda app: app.approval_type=='mandatory' and app.position_index > latest_approval.position_index and app.state=='pending' and app.approve_active==True)
            else:
                approval_ids_ready = fin_purchase.approver\
                    .filtered(lambda app: app.approval_type=='mandatory' and app.state=='pending' and app.approve_active==True)

            if approval_ids_ready:
                fin_purchase.next_approval_id = approval_ids_ready[0]
                fin_purchase.next_approval_ids = approval_ids_ready
                fin_purchase.next_approval_user_ids = approval_ids_ready[0].mapped('employee_user_id')

            overrule_states = ['DirectorOfFinance','AssistantOfOffice','DeputyOfOffice','SmallNote']
            #overrule_states = []
            #for state in ORIG_FIN_PURCHASE.STATE_SELECTION:
                #if state[0] in ['draft','sent','completed','cancelled', 'reject']:
                    #continue
                #overrule_states.append(state[0])

            if fin_purchase.state in overrule_states:
                #fin_purchase.next_approval_user_ids |= fin_purchase.approver.sorted(lambda app: app.position_index)[-1].mapped('employee_user_id')
                fin_purchase.next_approval_user_ids |= fin_purchase.approver\
                    .filtered(lambda app: app.approve_active==True)\
                    .sorted(lambda app: app.position_index)[-1].mapped('employee_user_id')

    @api.depends('next_approval_id', 'next_approval_user_ids', 'state', 'trigger')
    def _compute_can_approve(self):
        print("FIN_PURCHASE._compute_can_approve",self)
        for fin_purchase in self:
            #if self.env.user == fin_purchase.next_approval_id.employee_user_id:
            if self.env.user in fin_purchase.next_approval_user_ids:
                fin_purchase.can_approve = True
            else:
                fin_purchase.can_approve = False
            # force admin can approve
            if self.env.user.id == 1 and fin_purchase.next_approval_id:
                fin_purchase.can_approve = True

    @api.multi
    @api.depends('state', 'approver', 'next_approval_id', 'trigger', 'approver.position_index', 'approver.approve_step',
        'approver.employee_id', 'approver.employee_id.user_id', 'approver.employee_user_id',
        'approver.action_date', 'approver.state', 'approver.approval_type')
    def _compute_next_comment(self):
        print("FIN_PURCHASE._compute_next_comment",self)
        for fin_purchase in self:
            approval_ids = self.env['fw_pfb_fin_system_purchase_approver']
            approval_ids |= fin_purchase.approver\
                .filtered(lambda app: app.approve_active and app.approval_type=='comment' and app.approve_step <= fin_purchase.next_approval_id.approve_step and (not app.state or app.state=='pending'))
            approval_ids |= fin_purchase.approver.filtered(lambda app: app.approval_type=='comment') and fin_purchase.approver.filtered(lambda app: app.approval_type=='comment')[-1]
            fin_purchase.next_comment_ids = approval_ids.sorted(lambda app: app.position_index)
            if fin_purchase.next_comment_ids:
                fin_purchase.next_comment_user_ids = fin_purchase.next_comment_ids.mapped('employee_user_id')

    @api.depends('next_comment_ids', 'next_comment_user_ids', 'next_comment_ids.employee_user_id', 'state', 'trigger')
    def _compute_can_comment(self):
        print("FIN_PURCHASE._compute_can_comment",self)
        for fin_purchase in self:
            if self.env.user in fin_purchase.next_comment_user_ids:
                fin_purchase.can_comment = True
            else:
                fin_purchase.can_comment = False
            # force admin can approve
            if self.env.user.id == 1 and fin_purchase.next_comment_ids:
                fin_purchase.can_comment = True

    @api.multi
    @api.depends('purchase_order_ids')
    def _get_purchase_order_datas(self):
        print("FIN_PURCHASE._get_purchase_order_datas",self)
        for fin_purchase in self:
            fin_purchase.purchase_order_count = len(fin_purchase.purchase_order_ids)

    @api.model
    def create(self, vals):
        print("FIN_PURCHASE.create",vals)
        return super(fw_pfb_FS_purchase, self).create(vals)

    @api.multi
    def write(self, vals):
        print("FIN_PURCHASE.write", self, vals)
        return super(fw_pfb_FS_purchase, self).write(vals)

    @api.multi
    def action_create_purchase_order(self):
        print("FIN_PURCHASE.action_create_purchase_order", self)
        for obj in self:
            setting = self.env['fw_pfb_fin_settings2'].sudo().search([], limit=1)
            partner = setting.default_fin_purchase_partner_id
            if not partner:
                raise UserError(_('There is no default partner to create puchase order, please contact administrator'))
            now = fields.Datetime.now()
            po_lines = [(5, 0, 0)]
            for line in obj.fin_lines:
                po_line_vals = {
                    'product_id': line.product_id.id,
                    'name': line.description or line.product_id.name_get()[0][1],
                    'date_planned': now,
                    'product_qty': line.product_uom_qty or 0,
                    'product_uom': line.product_uom and line.product_uom.id or line.product_id.uom_po_id.id,
                    'price_unit': line.price_unit or 0.0,
                    'taxes_id': [(6, 0, line.product_id.supplier_taxes_id.ids)],
                }
                po_lines.append((0, 0, po_line_vals))
            po_vals = {
                'partner_id': partner.id,
                'date_order': now,
                'currency_id': self.env.user.company_id.currency_id.id,
                'doc_type': self.env['fw_ksp_po_doc_type'].search([], limit=1).id,
                'date_planned': now,
                'origin': obj.fin_no or obj.name_get()[0][1],
                'reference': obj.fin_no or obj.name_get()[0][1],
                'fin_purchase_id': obj.id,
                'order_line': po_lines,
            }
            po_id = self.env['purchase.order'].create(po_vals)
        return True

    @api.multi
    def action_view_purchase_orders(self):
        print("FIN_PURCHASE.action_view_purchase_orders",self)
        orders = self.mapped('purchase_order_ids')
        action = self.env.ref('purchase.purchase_rfq').read()[0]
        action['context'] = {}
        if orders:
            action['domain'] = [('id', 'in', orders.ids)]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def action_set_draft(self):
        print("FIN_PURCHASE.action_set_draft",self)
        self.write({'state':'draft'})

    @api.multi
    def action_set_done(self):
        print("FIN_PURCHASE.action_set_done",self)
        self.write({'state':'completed'})

    @api.multi
    def action_set_cancel(self):
        print("FIN_PURCHASE.action_set_cancel",self)
        self.write({'state':'cancelled'})

    @api.onchange('flow_template')
    def _onchange_flow_template(self):
        print("FIN_PURCHASE._onchange_flow_template",self)
        self.approver = False
        template_id = False
        if self.flow_template:
            template_id = self.flow_template.id
        template = self.env['fw_pfb_flow_template'].browse(template_id)
        if template and template.approve_line:
            for line in template.approve_line:
                data = {
                    "employee_id" : line.emp_name.id,
                    "fin_position" : line.position,
                    "approve_active" : line.data_activate,
                    "approve_position" : line.approve_position,
                    "position_index" : line.position_index,
                    "approval_type" : line.approval_type,
                    "approve_step" : line.approve_step,
                }
                if line.data_activate :
                    data["state"] = "pending"
                self.approver += self.approver.new(data)

    @api.multi
    def button_trigger(self):
        print("FIN_PURCHASE.button_trigger",self)
        for obj in self:
            obj.trigger = randrange(1000001)
        return True

    @api.multi
    def action_set_approve(self, note=""):
        print("FIN_PURCHASE.action_set_approve",self)
        for fin_purchase in self:
            approval = fin_purchase.next_approval_id

            if self.env.user != approval.user_id:
                if self.env.user.id == 1:
                    pass
                elif self.env.user in fin_purchase.next_approval_user_ids:
                    approval = fin_purchase.next_approval_ids.filtered(lambda app: app.employee_id.user_id == self.env.user)[0]
                else:
                    raise UserError(_('Only authorized person to approve or action'))

            if approval:
                if len(approval) > 1:
                    approval = approval[0]
                if approval.approval_type == 'mandatory':
                    pass
                if approval.approval_type == 'optional':
                    pass
                if approval.approval_type == 'comment':
                    raise UserError(_('Need to Comment'))
                approval.write({
                    'state': 'approve',
                    'action_date': fields.Datetime.now(),
                    'user_id': self.env.uid,
                    'memo': note,
                })
                approval.update_fin_status()
            else:
                latest_approval = fin_purchase.approver.sorted(lambda app: app.position_index)[-1]
                if self.env.user == latest_approval.mapped('employee_user_id') and not latest_approval.approve_active:
                    latest_approval.write({
                        'action_date': fields.Datetime.now(),
                        'user_id': self.env.uid,
                        'memo': note,
                    })
        return True

    @api.multi
    def action_set_reject(self, note=""):
        print("FIN_PURCHASE.action_set_reject",self)
        for fin_purchase in self:
            approval = fin_purchase.next_approval_id

            if self.env.user != approval.user_id:
                if self.env.user.id == 1:
                    pass
                elif self.env.user in fin_purchase.next_approval_user_ids:
                    approval = fin_purchase.next_approval_ids.filtered(lambda app: app.employee_id.user_id == self.env.user)
                else:
                    raise UserError(_('Only authorized person to approve or action'))

            if approval.approval_type == 'mandatory':
                pass
            if approval.approval_type == 'optional':
                pass
            if approval.approval_type == 'comment':
                raise UserError(_('Need to Comment'))
            if not note:
                raise UserError(_('Please input reason for reject'))
            approval.write({
                'state': 'reject',
                'action_date': fields.Datetime.now(),
                'user_id': self.env.uid,
                'memo': note,
            })
            fin_purchase.set_fin_purchase_to_reject()
            fin_purchase.action_generate_mail_to_reject()
        return True

    @api.multi
    def action_set_comment(self, note=""):
        print("FIN_PURCHASE.action_set_comment",self)
        for fin_purchase in self:
            approval = fin_purchase.next_comment_ids and fin_purchase.next_comment_ids[0] or False

            if self.env.user != approval.user_id:
                if self.env.user.id == 1:
                    pass
                elif self.env.user in fin_purchase.next_comment_user_ids:
                    approval = fin_purchase.next_comment_ids.filtered(lambda app: app.employee_id.user_id == self.env.user)
                else:
                    raise UserError(_('Only authorized person to comment or action'))

            if approval:
                if len(approval) > 1:
                    approval = approval[0]
                if approval.approval_type == 'mandatory':
                    raise UserError(_('Need to Approve / Reject'))
                if approval.approval_type == 'optional':
                    pass
                if approval.approval_type == 'comment':
                    pass
                if not note:
                    raise UserError(_('Please input Note/Comment'))
                approval.write({
                    'state': 'comment',
                    'action_date': fields.Datetime.now(),
                    'user_id': self.env.uid,
                    'memo': note,
                })
                approval.update_fin_status()
            else:
                latest_approval = fin_purchase.approver.sorted(lambda app: app.position_index)[-1]
                if self.env.user == latest_approval.mapped('employee_user_id') and not latest_approval.approve_active:
                    latest_approval.write({
                        'action_date': fields.Datetime.now(),
                        'user_id': self.env.uid,
                        'memo': note,
                    })
        return True

    @api.multi
    def set_fin_purchase_to_reject(self):
        print("FIN_PURCHASE.set_fin_purchase_to_reject",self)
        for fin_purchase in self:
            fin_purchase.check_reject = True
            fin_purchase.has_history = True
            fin_purchase.state = "reject"
        return True

    @api.multi
    def fin_set_to_draft(self):
        res = super(fw_pfb_FS_purchase, self).fin_set_to_draft()
        if self.approver:
            self.approver.write({'user_id': ''})
        return res

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        env_fin = self.env['fw_pfb_fin_system_purchase']
        env_fin_approver = self.env['fw_pfb_fin_system_purchase_approver']
        params = self._context.get('params')
        checkRule = False
        if params:
            if "action" in params:
               if params["action"] == 1168:
                   checkRule = True
        res = super(fw_pfb_FS_purchase, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

        if checkRule:
            fin_purchase_domain = [
                ('state','not in',['draft','cancelled','reject', 'completed']),
            ]
            fin_list = env_fin.search(fin_purchase_domain)
            to_hide_fin_list = env_fin.search([('id','not in',fin_list.ids)])
            if to_hide_fin_list:
                to_hide_fin_list.write({'show_fin': False})
            print("FOUND-FIN-PURCHASE >>>>>", len(fin_list))
            for fin in fin_list:
                fin_user = []

                if fin.check_reject != True :
                    if fin.next_approval_user_ids:
                        fin_user += fin.next_approval_user_ids.ids
                    if fin.next_comment_user_ids:
                        fin_user += fin.next_comment_user_ids.ids

                if self._uid in fin_user:
                    if not fin.show_fin : # if show_fin is False
                        fin.show_fin = True
                else:
                    if fin.show_fin : # if show_fin is True
                        fin.show_fin = False
        return res

    @api.model
    def cron_action_generate_mail_to_approve(self):
        return self.action_generate_mail_to_approve()

    @api.multi
    def action_generate_mail_to_approve(self):
        # schedule on 10:00 and 14:00
        FIN_PURCHASE = self.env['fw_pfb_fin_system_purchase']
        EMAIL = self.env['mail.mail']
        user_to_approve = {}

        mail_server_id = self.env['ir.config_parameter'].sudo().get_param('default_outgoing_mail_server') or False
        if not mail_server_id:
            mail_server_id = self.env['ir.mail_server'].search([], limit=1, order='sequence') and self.env['ir.mail_server'].search([], limit=1, order='sequence').id or False

        email_from = self.env['ir.config_parameter'].sudo().get_param('default_email_from') or False
        email_cc = self.env['ir.config_parameter'].sudo().get_param('default_email_cc') or False

        domain = [
            ('state', 'not in', ['draft','completed','cancelled','reject']),
            ('next_approval_user_ids', '!=', False),
        ]
        fin_purchase_to_approve_ids = FIN_PURCHASE.search(domain)
        print("action_generate_mail_to_approve",fin_purchase_to_approve_ids)

        for fin_purchase in fin_purchase_to_approve_ids:
            users = fin_purchase.mapped('next_approval_user_ids')
            for user in users:
                user_to_approve.setdefault(user, FIN_PURCHASE)
                user_to_approve[user] |= fin_purchase

        now = datetime.now()
        date_show = now.date().strftime("%Y-%m-%d")
        time_show = (now + timedelta(hours=7)).strftime("%H:%M")

        for user, docs in user_to_approve.items():
            message = u"<b>วันที่ "+ date_show +" "+ time_show  +u"</b>"
            message += u"<br/>"
            message += u"<br/>"
            message += u"คุณมี FIN-PURCHASE ใหม่ที่ต้องอนุมัติ จำนวน "+ str(len(docs)) +u" รายการ"
            message += u"<br/>"
            for doc_name in docs.sorted(lambda d: d.fin_no).mapped('fin_no'):
                doc_name = doc_name or "/"
                message += u""+ doc_name or "/" +"<br/>"
            message += u"<br/>"
            message += u"""<font style="font-size: 14px;">โปรดเข้าสู่ระบบเพื่อตรวจสอบ</font>"""
            message += u"<br/>"
            message += u"<br/>"
            message += u"""<font style="font-size: 14px;">ระบบจะส่ง e-mail อัตโนมัติ ในเวลา 10:00 น. ของทุกวัน และจะส่งอีกครั้งในเวลา 14:00 น. หากมีรายการใหม่เพิ่ม</font>"""

            email_to = user.partner_id.email or (user.employee_ids and user.employee_ids[0].es_email or False) or False
            if email_to and 'frontware' in email_to:
                email_to = False

            if email_to:
                values = {
                    'email_from': email_from,
                    'email_to': email_to,
                    'email_cc': email_cc or '',
                    'message_type': 'email',
                    'auto_delete': False,
                    'mail_server_id': mail_server_id,
                    'subject': u'FIN-PURCHASE สรุปรายการที่รออนุมัติ',
                    'body_html': message,
                    'state': 'outgoing',
                }
                email = EMAIL.sudo().create(values)
                EMAIL |= email

        # email send now
        db_name = self.env['ir.config_parameter'].sudo().get_param('database.name') or ''
        if self.env.cr.dbname == db_name:
            if EMAIL:
                EMAIL.send()

        return True

    @api.model
    def cron_action_generate_mail_to_comment(self):
        return self.action_generate_mail_to_comment()

    @api.multi 
    def action_generate_mail_to_comment(self):
        # schedule on 10:00 and 14:00
        FIN_PURCHASE = self.env['fw_pfb_fin_system_purchase']
        EMAIL = self.env['mail.mail']
        user_to_comment = {}

        mail_server_id = self.env['ir.config_parameter'].sudo().get_param('default_outgoing_mail_server') or False
        if not mail_server_id:
            mail_server_id = self.env['ir.mail_server'].search([], limit=1, order='sequence') and self.env['ir.mail_server'].search([], limit=1, order='sequence').id or False

        email_from = self.env['ir.config_parameter'].sudo().get_param('default_email_from') or False
        email_cc = self.env['ir.config_parameter'].sudo().get_param('default_email_cc') or False

        domain = [
            ('state', 'not in', ['draft','completed','cancelled','reject']),
            ('next_comment_user_ids', '!=', False),
        ]
        fin_purchase_to_comment_ids = FIN_PURCHASE.search(domain)
        print("action_generate_mail_to_comment",fin_purchase_to_comment_ids)

        for fin_purchase in fin_purchase_to_comment_ids:
            users = fin_purchase.mapped('next_comment_user_ids')
            for user in users:
                user_to_comment.setdefault(user, FIN_PURCHASE)
                user_to_comment[user] |= fin_purchase

        now = datetime.now()
        date_show = now.date().strftime("%Y-%m-%d")
        time_show = (now + timedelta(hours=7)).strftime("%H:%M")

        for user, docs in user_to_comment.items():
            message = u"<b>วันที่ "+ date_show +" "+ time_show  +u"</b>"
            message += u"<br/>"
            message += u"<br/>"
            message += u"คุณมี FIN-PURCHASE ใหม่ที่สามารถออกความเห็นได้ จำนวน "+ str(len(docs)) +u" รายการ"
            message += u"<br/>"
            for doc_name in docs.sorted(lambda d: d.fin_no).mapped('fin_no'):
                doc_name = doc_name or "/"
                message += u""+ doc_name +"<br/>"
            message += u"<br/>"
            message += u"""<font style="font-size: 14px;">โปรดเข้าสู่ระบบเพื่อตรวจสอบ</font>"""
            message += u"<br/>"
            message += u"<br/>"
            message += u"""<font style="font-size: 14px;">ระบบจะส่ง e-mail อัตโนมัติ ในเวลา 10:00 น. ของทุกวัน และจะส่งอีกครั้งในเวลา 14:00 น. หากมีรายการใหม่เพิ่ม</font>"""

            email_to = user.partner_id.email or (user.employee_ids and user.employee_ids[0].es_email or False) or False
            if email_to and 'frontware' in email_to:
                email_to = False

            if email_to:
                values = {
                    'email_from': email_from,
                    'email_to': email_to,
                    'email_cc': email_cc or '',
                    'message_type': 'email',
                    'auto_delete': False,
                    'mail_server_id': mail_server_id,
                    'subject': u'FIN-PURCHASE สรุปรายการที่รอความเห็น',
                    'body_html': message,
                    'state': 'outgoing',
                }
                email = EMAIL.sudo().create(values)
                EMAIL |= email

        # email send now
        db_name = self.env['ir.config_parameter'].sudo().get_param('database.name') or ''
        if self.env.cr.dbname == db_name:
            if EMAIL:
                EMAIL.send()

        return True

    @api.multi 
    def action_generate_mail_to_reject(self):
        # schedule now when rejected
        print("action_generate_mail_to_reject",self)
        FIN_PURCHASE = self.env['fw_pfb_fin_system_purchase']
        EMAIL = self.env['mail.mail']
        user_to_comment = {}

        mail_server_id = self.env['ir.config_parameter'].sudo().get_param('default_outgoing_mail_server') or False
        if not mail_server_id:
            mail_server_id = self.env['ir.mail_server'].search([], limit=1, order='sequence') and self.env['ir.mail_server'].search([], limit=1, order='sequence').id or False

        email_from = self.env['ir.config_parameter'].sudo().get_param('default_email_from') or False
        email_cc = self.env['ir.config_parameter'].sudo().get_param('default_email_cc') or False

        now = datetime.now()
        date_show = now.date().strftime("%Y-%m-%d")
        time_show = (now + timedelta(hours=7)).strftime("%H:%M")

        for fin_purchase in self:
            doc_name = fin_purchase.fin_no or "/"
            message = u"<b>วันที่ "+ date_show +" "+ time_show  +u"</b>"
            message += u"<br/>"
            message += u"<br/>"
            message += u"คุณมี FIN-PURCHASE ที่ถูกปฏิเสธ จำนวน "+ str('1') +u" รายการ"
            message += u"<br/>"
            message += u""+ doc_name +"<br/>"
            message += u"<br/>"
            message += u"""<font style="font-size: 14px;">โปรดเข้าสู่ระบบเพื่อตรวจสอบ</font>"""
            message += u"<br/>"
            message += u"<br/>"
            message += u"""<font style="font-size: 14px;">regards</font>"""
            message += u"<br/>"
            message += u"<br/>"
            message += u"""<font style="font-size: 14px;">Administrator</font>"""

            user = fin_purchase.requester.user_id
            email_to = user.partner_id.email or (user.employee_ids and user.employee_ids[0].es_email or False) or False
            if email_to and 'frontware' in email_to:
                email_to = False

            if email_to:
                values = {
                    'email_from': email_from,
                    'email_to': email_to,
                    'email_cc': email_cc or '',
                    'message_type': 'email',
                    'auto_delete': False,
                    'mail_server_id': mail_server_id,
                    'subject': u'FIN-PURCHASE สรุปรายการที่ถูกปฏิเสธ',
                    'body_html': message,
                    'state': 'outgoing',
                }
                email = EMAIL.sudo().create(values)
                EMAIL |= email

        # email send now
        db_name = self.env['ir.config_parameter'].sudo().get_param('database.name') or ''
        if self.env.cr.dbname == db_name:
            if EMAIL:
                EMAIL.send()

        return True

    @api.multi
    def get_action_fin_purchase_to_approve(self):
        action = {
            'name': _('Pending'),
            'type': "ir.actions.act_window",
            'res_model': "fw_pfb_fin_system_purchase",
            'view_id': self.env.ref('fin_system.fin_system_purchase_pending_tree_view').id,
            'view_type': "form",
            'view_mode': "tree,form",
        }
        action['views'] = [
            (self.env.ref('fin_system.fin_system_purchase_pending_tree_view').id, 'tree'),
            (self.env.ref('fin_system.fin_system_purchase_request_form_view').id, 'form'),
        ]
        action['domain'] = """[
            ('state','not in',['draft', 'cancelled', 'reject', 'completed']),
            '|', ('next_approval_user_ids', 'in', %s),
                 ('next_comment_user_ids', 'in', %s),
        ]""" %(self.env.user.ids, self.env.user.ids)
        return action

class fw_pfb_FS_purchaseLines(models.Model):
    _inherit = 'fw_pfb_fin_system_purchase_line'

    @api.model
    def create(self, vals):
        print("FIN_PURCHASE_LINE.create",vals)
        return super(fw_pfb_FS_purchaseLines, self).create(vals)

    @api.multi
    def write(self, vals):
        print("FIN_PURCHASE_LINE.write", self, vals)
        return super(fw_pfb_FS_purchaseLines, self).write(vals)

class fw_pfb_FS_purchaseApprover(models.Model):
    _inherit = 'fw_pfb_fin_system_purchase_approver'

    approval_type = fields.Selection([
        #('optional', 'Approves, but the approval is optional'),
        ('mandatory', 'Is required to approve'),
        ('comment', 'Comments only'),
        ], 'Approval Type',
        default='mandatory', required=True)
    approve_step = fields.Integer(string='Step', default=0, required=True)
    trigger = fields.Integer(string="trigger")
    user_id = fields.Many2one('res.users', string="Approved by")
    state = fields.Selection(selection_add=[('comment', 'Comment')])
    can_reset = fields.Boolean('Can Reset', compute='_compute_can_reset')

    def _compute_can_reset(self):
        print("FIN_PURCHASE_APPROVER._compute_can_reset",self)
        for approval in self:
            approval.can_reset = False
            last_approval = approval.fin_id.approver.filtered(lambda app: app.approval_type=='mandatory' and app.approve_active==True).sorted(lambda app: app.position_index)
            if last_approval:
                last_approval = last_approval[-1]
                if last_approval == approval and last_approval.state != 'pending':
                    if self.env.user.id in last_approval.employee_user_id.ids:
                        approval.can_reset = True
                    else:
                        approval.can_reset = False
            # force admin can reset for all
            if self.env.user.id == 2:
                approval.can_reset = True

    @api.multi
    @api.depends('employee_id','fin_position', 'approve_step')
    def name_get(self):
        print("FIN_PURCHASE_APPROVER.name_get",self)
        res = []
        for obj in self:
            name = obj.employee_id.display_name
            if obj.fin_position:
                fin_position = dict(obj._fields.get('fin_position').selection).get(obj.fin_position)
                name = "%s: %s"%(fin_position, name)
            if obj.approve_step:
                name = "Step %s. %s"%(obj.approve_step, name)
            res.append((obj.id, name))
        return res and res or super(fw_pfb_FS_purchaseApprover, self).name_get()

    @api.multi
    def update_fin_status(self):
        print("FIN_PURCHASE_APPROVER.update_fin_status",self)
        for approval_id in self:
            if approval_id.approve_position == 'DirectorOfDepartment':
                if approval_id.state == 'approve':
                    approval_id.fin_id.state = 'DirectorOfDepartment'
                    approval_id.fin_id.target_approver = 'ManagerOfStock'
            elif approval_id.approve_position == 'ManagerOfStock':
                if approval_id.state == 'approve':
                    approval_id.fin_id.state = 'ManagerOfStock'
                    approval_id.fin_id.target_approver = 'AssistantOfOffice'
            elif approval_id.approve_position == 'AssistantOfOffice':
                if approval_id.state == 'approve':
                    approval_id.fin_id.state = 'AssistantOfOffice'
                    approval_id.fin_id.target_approver = 'DeputyOfOffice'
            elif approval_id.approve_position == 'DeputyOfOffice':
                if approval_id.state == 'approve':
                    approval_id.fin_id.state = 'DeputyOfOffice'
                    approval_id.fin_id.target_approver = 'SmallNote'
            elif approval_id.approve_position == 'SmallNote':
                if approval_id.state == 'approve':
                    approval_id.fin_id.state = 'SmallNote'
                    approval_id.fin_id.target_approver = 'DirectorOfOffice'
            elif approval_id.approve_position == 'DirectorOfOffice':
                if approval_id.state == 'approve':
                    approval_id.fin_id.state = 'DirectorOfOffice'
                    approval_id.fin_id.target_approver = 'DirectorOfOffice'
        return True

    @api.multi
    def button_trigger(self):
        print("FIN_PURCHASE_APPROVER.button_trigger",self)
        for obj in self:
            obj.trigger = randrange(1000001)
        return True

    @api.multi
    def action_reset_approval(self):
        print("FIN_PURCHASE_APPROVER.button_reset_approval",self)
        for approval in self:
            approval.write({
                'memo': '',
                'action_date': False,
                'state': 'pending',
                'user_id': False,
            })
            lastest_approval_id = approval.fin_id.approver.filtered(lambda app: app.approval_type=='mandatory' and app.state=='approve' and app.approve_active==True)
            lastest_approval_id.update_fin_status()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

class WizardFINPurchaseApproval(models.TransientModel):
    """
    This wizard will Approve/Reject/Comment for FIN-PURCHASE
    """
    _name = "wizard.fin.purchase.approval"
    _description = "FIN-PURCHASE Approval"

    def _default_next_approval(self):
        print("_default_next_approval",self)
        res = False
        if self._context.get('next_approval_id'):
            res = self.env['fw_pfb_fin_system_purchase_approver'].browse(self._context.get('next_approval_id'))
        return res

    def _default_next_comment(self):
        print("_default_next_comment",self)
        fin_purchase_ids = self.env['fw_pfb_fin_system_purchase'].browse(self._context.get('active_ids'))
        next_comment_ids = fin_purchase_ids.mapped('next_comment_ids').sorted(lambda x: x.id).ids
        return next_comment_ids

    def _default_next_comment_user(self):
        print("_default_next_comment_user",self)
        fin_purchase_ids = self.env['fw_pfb_fin_system_purchase'].browse(self._context.get('active_ids'))
        next_comment_user_ids = fin_purchase_ids.mapped('next_comment_ids').sorted(lambda x: x.id).mapped('employee_user_id')
        return next_comment_user_ids

    next_approval_id = fields.Many2one('fw_pfb_fin_system_purchase_approver', string='Next Approval', default=_default_next_approval)
    employee_user_id = fields.Many2one('res.users', string='Requested User', related="next_approval_id.employee_user_id")

    next_comment_ids = fields.Many2many('fw_pfb_fin_system_purchase_approver', string='Next Comment',
        relation="wizard_fin_purchase_to_approver_rel", column1='wizard_id', column2='approval_id',
        default=_default_next_comment)
    next_comment_user_ids = fields.Many2many('res.users', string='Next Comment Users', default=_default_next_comment_user)

    approval_type = fields.Selection([
        #('optional', 'Approves, but the approval is optional'),
        ('mandatory', 'Is required to approve'),
        ('comment', 'Comments only'),
        ], 'Approval Type',
        related="next_approval_id.approval_type")
    note = fields.Text(string="Memo", required=True)

    @api.multi
    def action_approve(self):
        print("WIZARD_FIN_PURCHASE_APPROVAL.action_approve",self)
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        fin_purchase_ids = self.env['fw_pfb_fin_system_purchase'].browse(active_ids)
        for fin_purchase in fin_purchase_ids:
            fin_purchase.action_set_approve(note=self.note)
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def action_reject(self):
        print("WIZARD_FIN_PURCHASE_APPROVAL.action_reject",self)
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        fin_purchase_ids = self.env['fw_pfb_fin_system_purchase'].browse(active_ids)
        for fin_purchase in fin_purchase_ids:
            fin_purchase.action_set_reject(note=self.note)
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def action_comment(self):
        print("WIZARD_FIN_PURCHASE_APPROVAL.action_comment",self)
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        fin_purchase_ids = self.env['fw_pfb_fin_system_purchase'].browse(active_ids)
        for fin_purchase in fin_purchase_ids:
            fin_purchase.action_set_comment(note=self.note)
        return {'type': 'ir.actions.act_window_close'}
