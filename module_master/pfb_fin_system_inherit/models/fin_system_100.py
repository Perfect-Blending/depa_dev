from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError



class fw_pfb_FS100_Approver(models.Model):
    _inherit = 'fw_pfb_fin_system_100_approver'

    def _compute_can_reset(self):
        for approval in self:
            approval.can_reset = False
            last_approval = approval.fin_id.approver.filtered(
                lambda app: app.approval_type == 'mandatory' and app.approve_active == True).sorted(
                lambda app: app.position_index)
            if last_approval:
                last_approval = last_approval[-1]
                if last_approval == approval and last_approval.state != 'pending':
                    if self.env.user.id in last_approval.employee_user_id.ids:
                        approval.can_reset = True
                    else:
                        approval.can_reset = False
            approval.can_reset = True
            # force admin can reset for all
            # if self.env.user.id == 2:
            #     approval.can_reset = True


class fw_pfb_FS100_inherit(models.Model):
    _inherit = 'fw_pfb_fin_system_100'

    # @api.multi
    # def fin_create_pr(self):
    #     if self.state == 'completed':
    #         vals = {}
    #         proj_n_plan = None
    #         request_lines = {}
    #         i = 0
    #         date_approve = fields.Datetime()
    #         for line_approve in self.approver:
    #             if line_approve.action_date:
    #                 date_approve = line_approve.action_date
    #         for line in self.fin_lines:
    #             if line:
    #                 i += 1
    #                 if line.projects_and_plan:
    #                     proj_n_plan = line.projects_and_plan.id
    #
    #                 request_lines[i] = {
    #                     'product_id': line.product_id.id,
    #                     'name': line.description,
    #                     'product_qty': line.product_uom_qty,
    #                     'product_uom_id': line.product_uom.id,
    #                     'analytic_account_id': proj_n_plan,
    #                     'estimated_cost': line.price_unit,
    #                 }
    #
    #                 vals = {
    #                     'fin_id': self.id,
    #                     'fin_number': self.id,
    #                     'date_approve': date_approve,
    #                     'requested_by': self.requester.user_id.id,
    #                     'department_id': self.department.id,
    #                     'description': self.objective,
    #                 }
    #
    #                 # Declare res_model use for attachment stamp
    #                 attachment_res_model = 'purchase.request'
    #
    #                 # Prepare attachment data
    #                 if self.attachment_base_price:
    #                     vals['pr_ck'] = True
    #                     attribute_pr_id = {}
    #                     for key, attachment in enumerate(self.attachment_base_price):
    #                         attribute_pr_id[key] = self.env['ir.attachment'].create({
    #                             'name': attachment.name,
    #                             'datas': attachment.datas,
    #                             'datas_fname': attachment.datas_fname,
    #                             'res_model': attachment_res_model,
    #                             'res_id': 0,
    #                         }).id
    #                 else:
    #                     raise UserError('No base price attachment')
    #                 if self.attachment_work_scope:
    #                     vals['pr2_ck'] = True
    #                     middle_price_id = {}
    #                     for key, attachment in enumerate(self.attachment_work_scope):
    #                         middle_price_id[key] = self.env['ir.attachment'].create({
    #                             'name': attachment.name,
    #                             'datas': attachment.datas,
    #                             'datas_fname': attachment.datas_fname,
    #                             'res_model': attachment_res_model,
    #                             'res_id': 0,
    #                         }).id
    #                 else:
    #                     raise UserError('No work scope attachment')
    #                 if self.attachment_participants:
    #                     vals['pr3_ck'] = True
    #                     attachment_participants_id = {}
    #                     for key, attachment in enumerate(self.attachment_participants):
    #                         attachment_participants_id[key] = self.env['ir.attachment'].create({
    #                             'name': attachment.name,
    #                             'datas': attachment.datas,
    #                             'datas_fname': attachment.datas_fname,
    #                             'res_model': attachment_res_model,
    #                             'res_id': 0,
    #                         }).id
    #                 else:
    #                     raise UserError('No participants attachment')
    #                 if self.attachment_memo:
    #                     vals['pr4_ck'] = True
    #                     attachment_memo_id = {}
    #                     for key, attachment in enumerate(self.attachment_memo):
    #                         attachment_memo_id[key] = self.env['ir.attachment'].create({
    #                             'name': attachment.name,
    #                             'datas': attachment.datas,
    #                             'datas_fname': attachment.datas_fname,
    #                             'res_model': attachment_res_model,
    #                             'res_id': 0,
    #                         }).id
    #                 ###
    #
    #                 pr_obj = self.env['purchase.request'].search([
    #                     ('fin_id', '=', self.id),
    #                 ], limit=1)
    #                 if pr_obj:
    #                     pr_obj.write(vals)
    #                     pr_obj.line_ids.unlink()
    #                     for line in request_lines:
    #                         request_lines[line]['request_id'] = pr_obj.id
    #                         pr_obj.line_ids.create(request_lines[line])
    #                     res = pr_obj
    #                 else:
    #                     res = self.env['purchase.request'].create(vals)
    #                     # INSERT attachment to attribute_pr field
    #                     if 'pr_ck' in vals:
    #                         for api in attribute_pr_id:
    #                             self.env.cr.execute(
    #                                 """INSERT INTO attachment_attribute_pr_rel(attachment_attribute_pr_id, attachment_id)
    #                                 VALUES(%d, %d);""" %
    #                                 (res.id, attribute_pr_id[api])
    #                             )
    #                     # INSERT attachment to middle_price field
    #                     if 'pr2_ck' in vals:
    #                         for mpi in middle_price_id:
    #                             self.env.cr.execute(
    #                                 """INSERT INTO attachment_middle_price_rel(attachment_middle_price_id, attachment_id)
    #                                 VALUES(%d, %d);""" %
    #                                 (res.id, middle_price_id[mpi])
    #                             )
    #                     # INSERT attachment to attribute_pr2 field
    #                     if 'pr3_ck' in vals:
    #                         for api in attachment_participants_id:
    #                             self.env.cr.execute(
    #                                 """INSERT INTO attachment_attribute_pr2_rel(attachment_attribute_pr2_id, attachment_id)
    #                                 VALUES(%d, %d);""" %
    #                                 (res.id, attachment_participants_id[api])
    #                             )
    #                     # INSERT attachment to attribute_pr3 field
    #                     if 'pr4_ck' in vals:
    #                         for ami in attachment_memo_id:
    #                             self.env.cr.execute(
    #                                 """INSERT INTO attachment_attribute_pr3_rel(attachment_attribute_pr3_id, attachment_id)
    #                                 VALUES(%d, %d);""" %
    #                                 (res.id, attachment_memo_id[ami])
    #                             )
    #
    #                     self.is_pr_created = True
    #                     for line in request_lines:
    #                         request_lines[line]['request_id'] = res.id
    #                         self.env['purchase.request.line'].create(request_lines[line])
    #
    #                 # res.attribute_pr.write({
    #                 #     'res_model': 'purchase.request',
    #                 #     'res_id': res.id,
    #                 # })
    #
    #         return {
    #             'name': "Purchase Request",
    #             'view_type': 'form',
    #             'view_mode': 'form',
    #             'res_model': 'purchase.request',
    #             'res_id': res.id,
    #             'type': 'ir.actions.act_window',
    #         }



class WizardFin100CarryOut(models.Model):
    _name = 'wizard.fin.100.carry.out'

    fin_100_id = fields.Many2one(
            'fw_pfb_fin_system_100'
    )
    fin_100_line_id = fields.Many2one(
            'fw_pfb_fin_system_100_line',
            verbose_name='FIN100 Line',
            domain="[('fin_id', '=', fin_100_id), ('balance', '>=', 0.0)]"
    )
    current_projects_and_plan_id = fields.Many2one(
            'account.analytic.account',
            verbose_name='Current Projects and plan'
    )
    current_fiscal_year = fields.Many2one(
            'fw_pfb_fin_system_fiscal_year',
            verbose_name='Current Fiscal year'
    )
    new_projects_and_plan_id = fields.Many2one(
            'account.analytic.account',
            verbose_name='New Projects and plan'
    )
    new_fiscal_year = fields.Many2one(
            'fw_pfb_fin_system_fiscal_year',
            verbose_name='New Fiscal year'
    )

    @api.multi
    def fin_100_carry_out_submit(self):
        if self.new_projects_and_plan_id:
            # Prevent user from select the same projects and plan
            if self.current_projects_and_plan_id.id == self.new_projects_and_plan_id.id:
                raise UserError('You select the same Projects and Plan')
            else:
                fin_100 = self.fin_100_id
                fin_100_line = self.fin_100_line_id
                current_balance = fin_100_line.balance
                # Create new FIN100 line
                # 2 steps
                # 1. Change current line price_unit by finding residual
                # (unit_price * qty) - balance
                balance_residual = (fin_100_line.price_unit * fin_100_line.product_uom_qty) - fin_100_line.balance
                fin_100_line.price_unit = balance_residual
                # 2. Set new line price_unit by latest balance and set a new projects and plan selected by User
                # QTY always set to 1
                new_line_data = {
                        'fin_100_state': fin_100_line.fin100_state,
                        'fin_id': fin_100.id,
                        'product_id': fin_100_line.product_id.id,
                        'product_uom_qty': 1,
                        'product_uom': fin_100_line.product_uom.id,
                        'price_unit': current_balance,
                        'projects_and_plan': self.new_projects_and_plan_id.id,
                }
                fin_100.fin_lines = [(0, 0, new_line_data)]
                # Call button_trigger to re-calculate value on fin_lines
                fin_100.button_trigger()
                


    @api.onchange('fin_100_line_id')
    def _onchange_fin_100_line(self):
        for rec in self:
            if rec.fin_100_line_id:
                rec.current_projects_and_plan_id = rec.fin_100_line_id.projects_and_plan.id
                rec.current_fiscal_year = rec.fin_100_line_id.fiscal_year.id

    @api.onchange('new_projects_and_plan_id')
    def _onchange_new_projects_and_plan(self):
        for rec in self:
            if rec.new_projects_and_plan_id:
                rec.new_fiscal_year = rec.new_projects_and_plan_id.fiscal_year.id

    
    @api.model
    def default_get(self, fields):
        res = super(WizardFin100CarryOut, self).default_get(fields)
        if self._context['active_model'] == 'fw_pfb_fin_system_100':
            fin_100_id = self._context['active_id']
            res.update({
                'fin_100_id': fin_100_id
            })
        return res
