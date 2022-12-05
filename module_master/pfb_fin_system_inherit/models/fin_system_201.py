from odoo import api, fields, models, _


class fw_pfb_FS201Inherit(models.Model):
    _inherit = 'fw_pfb_fin_system_201'

    fin_audit = fields.Boolean(string="ตรวจสอบแล้ว", )


class fw_pfb_FS201_Approver(models.Model):
    _inherit = 'fw_pfb_fin_system_201_approver'

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
