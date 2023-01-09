from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date

class kpi_dsm_pm_make_approval_wizard(models.TransientModel):
    _name = 'kpi_dsm_pm_make_approval_wizard'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    kpi_setting_dsm_pm_id = fields.Many2one(
        'kpi_setting_dsm_pm'
    )

    remark = fields.Text(
        string="ความคิดเห็น",
        help="กรอกเพื่อแสดงความคิดเห็น",
        required=True
    )

    current_state = fields.Char(
        string="สถานะ",
    )

    def action_approve(self):
        setting_dsm_pm_id = self.kpi_setting_dsm_pm_id
        approval_lines_count = len(setting_dsm_pm_id.kpi_setting_pm_approval_lines_ids)

        for line in setting_dsm_pm_id.kpi_setting_pm_lines_ids:
            if not line.is_done:
                raise ValidationError(_('คุณต้องตรวจข้อมูล KPI ครบทุกรายการก่อนทำการอนุมัติ'))
            # if not line.is_validated:
            #     raise ValidationError(_('คุณต้องตรวจข้อมูล KPI ครบทุกรายการก่อนทำการอนุมัติ'))

        # Is last approval
        # if setting_dsm_pm_id.approve_count < approval_lines_count:
        #     setting_dsm_pm_id.kpi_setting_pm_approval_lines_ids[approval_lines_count - 1].update({
        #         'approve_datetime': datetime.today(),
        #         'remark': self.remark,
        #         'status': 'done'
        #     })
        #     setting_dsm_pm_id.update({
        #         # 'current_approval_id': False,
        #         'state': 'draft',
        #     })
        #     setting_dsm_pm_id.approve_count += 1
        #
        # elif setting_dsm_pm_id.approve_count == approval_lines_count:
        setting_dsm_pm_id.kpi_setting_pm_approval_lines_ids[approval_lines_count-1].update({
            'approve_datetime': datetime.today(),
            'remark': self.remark,
            'status': 'done'
        })
        setting_dsm_pm_id.update({
            # 'current_approval_id': False,
            'state': 'completed',
        })

        # create kpi into each department
        users = self.env['hr.employee'].search([])
        print("11")
        print(users)

        for user in users:
            pm_setting_lines = []
            user_id = user.id

            pm_lines = self.env['kpi_user_lines'].search([
                ('kpi_user_lines_id.kpi_setting_pm_lines_id.id', '=', setting_dsm_pm_id.id),
                ('kpi_hr_user_id', '=', user_id),
            ])
            print(pm_lines)
            if pm_lines:
                fin = 0.0
                cus = 0.0
                inter = 0.0
                learn = 0.0
                for pm_line in pm_lines:
                    rec = pm_line.kpi_user_lines_id
                    # if rec.kpi_bsc == 'F':
                    #     fin += rec.kpi_weight
                    #     self.financial = fin
                    # elif rec.kpi_bsc == 'C':
                    #     cus += rec.kpi_weight
                    #     self.customer = cus
                    # elif rec.kpi_bsc == 'I':
                    #     inter += rec.kpi_weight
                    #     self.internal = inter
                    # else:
                    #     learn += rec.kpi_weight
                    #     self.learning = learn
                    # print(pm_line.kpi_user_lines_id.project_name)


                    pm_setting_lines.append((
                        0,
                        0,
                        {
                            'kpi_setting_group_lines_id': rec.id,
                            # 'kpi_code': rec.kpi_code,
                            'activity_name': pm_line.kpi_activity_id,
                            'activity_time': pm_line.kpi_time,
                            'activity_weight': pm_line.kpi_user_weight,
                            'user_id': pm_line.kpi_hr_user_id.user_id.id,
                            'project_id': pm_line.kpi_user_lines_id.project_name,
                            # 'kpi_unit': rec.kpi_unit.id,
                            # 'kpi_bsc': rec.kpi_bsc,
                            'project_budget': rec.project_budget,
                            # 'kpi_calculate': rec.kpi_calculate,
                            # 'kpi_definition': rec.kpi_definition,
                            # 'kpi_has_assistant': department_line.kpi_has_assistant,
                            # 'kpi_assistant_employee_id': department_line.kpi_assistant_employee_id.id,
                            'project_status': 'pending',
                            # 'kpi_pm_definition_lines_ids': [(6, 0, pm_line.kpi_pm_definition_line_ids.ids)]
                        }
                    ))
                # print("==")
                # print(user_id)


            # if pm_line.kpi_department_has_assign:
            #     manager_id = pm_line.kpi_department_assign_employee_id.user_id.id
            #         print(pm_line.kpi_hr_user_id.user_id.id)
                print(pm_line.kpi_user_lines_id.kpi_setting_pm_lines_id.department_id.id)
                self.env['kpi_setting_dsm_activity'].create({
                    'department_id': pm_line.kpi_user_lines_id.kpi_setting_pm_lines_id.department_id.id,
                    # 'financial': fin,
                    # 'customer': cus,
                    # 'internal': inter,
                    # 'learning': learn,
                    'current_approval_id': pm_line.kpi_hr_user_id.user_id.id,
                    'kpi_setting_activity_lines_ids': pm_setting_lines,
                    'kpi_setting_activity_approval_lines_ids': [(0, 0, {
                        'employee_id': pm_line.kpi_hr_user_id.department_id.manager_id.id,
                        'status': 'pending'
                    })],
                })


    # def action_adjustment(self):
    #     # print(self)
    #     setting_dsm_id = self.kpi_setting_dsm_group_id
    #     approval_lines_count = len(setting_dsm_id.kpi_setting_group_approval_lines_ids)
    #     setting_dsm_id.kpi_setting_group_approval_lines_ids[approval_lines_count - 1].update({
    #         'approve_datetime': datetime.today(),
    #         'remark': self.remark,
    #         'status': 'adjust'
    #     })
    #     setting_dsm_id.update({
    #         'current_approval_id': False,
    #         'state': 'adjust',
    #     })
    #     setting_dsm_id.approve_count = 0
    #
    # def action_reject(self):
    #     setting_dsm_id = self.kpi_setting_dsm_group_id
    #     approval_lines_count = len(setting_dsm_id.kpi_setting_group_approval_lines_ids)
    #     setting_dsm_id.kpi_setting_group_approval_lines_ids[approval_lines_count - 1].update({
    #         'approve_datetime': datetime.today(),
    #         'remark': self.remark,
    #         'status': 'reject'
    #     })
    #     setting_dsm_id.update({
    #         'current_approval_id': False,
    #         'state': 'rejected',
    #     })