from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date

class make_kpi_evaluate_wizard(models.TransientModel):
    _name = 'make_kpi_evaluate_wizard'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    kpi_main_id = fields.Many2one(
        'kpi_main'
    )
    evaluate_count = fields.Integer(
        string="Evaluate Count"
    )
    remark = fields.Text(
        string="ความคิดเห็น",
        help="กรอกเพื่อแสดงความคิดเห็น",
        required=True
    )
    action_status = fields.Selection(
        [
            ('confirm', 'ยืนยัน'),
            ('adjust', 'แก้ไข'),
        ],
        default='confirm'
    )

    def action_confirm_evaluation(self):
        kpi = self.kpi_main_id
        count = self.evaluate_count
        if kpi.evaluate_line_ids:
            evaluate_line_ids = kpi.evaluate_line_ids.sorted(lambda x: x.step)
            evaluate_line_ids[count - 1].update({
                'comment': self.remark,
                'evaluate_time': datetime.now(),
                'evaluate_status': '1'
            })
            kpi.message_post(
                body=str(kpi.kpi_no) + " ถูกประเมินแล้วโดย " + str(evaluate_line_ids[count - 1].employee_id.name))

            if len(kpi.evaluate_line_ids) == count:
                kpi.update({
                    'kpi_evaluating_user': False,
                    'state': 'done'
                })
                kpi.message_post(
                    body=f"{str(kpi.kpi_no)} ถูกประเมินเสร็จสิ้นแล้วโดยผู้ประเมินทั้ง {len(kpi.evaluate_line_ids)}  คน")
            else:
                evaluate_line_ids[count].update({
                    'comment': False,
                    'evaluate_time': False,
                    'evaluate_status': '0'
                })
                kpi.kpi_evaluating_user = evaluate_line_ids[count].employee_id.user_id.id
                kpi.evaluate_count = count + 1

            kpi.update({
                'is_current_evaluator': False
            })
        return {
            'type': 'ir.actions.act_window_close'
        }

    def action_adjust_evaluation(self):
        kpi = self.kpi_main_id
        count = self.evaluate_count
        if kpi.evaluate_line_ids:
            evaluate_line_ids = kpi.evaluate_line_ids.sorted(lambda x: x.step)
            if count >= 2:
                evaluate_line_ids[count - 1].update({
                    'comment': self.remark,
                    'evaluate_time': datetime.now(),
                    'evaluate_status': '3'
                })
                evaluate_line_ids[count - 2].update({
                    'comment': False,
                    'evaluate_time': False,
                    'evaluate_status': '0'
                })
                kpi.kpi_evaluating_user = evaluate_line_ids[count - 2].employee_id.user_id.id
                kpi.evaluate_count = count - 1

                kpi.message_post(
                    body=str(kpi.kpi_no) + " ถูกส่งกลับให้ผู้ประเมินก่อนหน้าแก้ไขโดย " + str(evaluate_line_ids[count - 1].employee_id.name))

                kpi.update({
                    'is_current_evaluator': False
                })

        return {
            'type': 'ir.actions.act_window_close'
        }
