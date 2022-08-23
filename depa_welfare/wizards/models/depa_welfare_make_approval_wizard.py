from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date

class depa_welfare_make_approval_wizard(models.TransientModel):
    _name = 'depa_welfare_make_approval_wizard'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    welfare_id = fields.Many2one(
        'depa_welfare'
    )

    remark = fields.Text(
        string="ความคิดเห็น",
        help="กรอกเพื่อแสดงความคิดเห็น",
        required=True
    )

    current_state = fields.Char()

    def _get_workflow_state(self):
        state = False
        flow_using = self.env['depa_welfare_flow_setting'].search([
            ('is_used', '=', True)
        ], limit=1)

        if flow_using:
            dicts = [{"step": int(line.step),"code":line.state.code, "name":line.state.name} for line in flow_using.workflow_process_ids]
            flow_sorted = sorted(dicts, key=lambda item: item["step"])
            state = [(line["code"], line["name"]) for line in flow_sorted]

        return state

    def action_approve(self):
        # print(self)
        has_reject_line = False
        for rec in self.welfare_id:
            for line in rec.depa_welfare_lines_ids:
                if line.is_hr_reject:
                    has_reject_line = True
                    break

        if has_reject_line:
            raise ValidationError(_('กรุณาตรวจสอบและกดยกเลิกการแก้ไขในแต่ละรายการก่อนส่งอนุมัติ'))

        approval_id = self.welfare_id.state_approval.id
        prevState = ""
        currentState = ""
        nextState = ""

        workflow_states = self._get_workflow_state()

        for i, workflow_state in enumerate(workflow_states):
            if workflow_state[0] == self.current_state:
                prevState = workflow_states[i][0]  # HR
                currentState = workflow_states[i + 1][0]  # HEAD HR
                nextState = workflow_states[i + 2][0]  # HEAD DEPART
                break

        print(prevState + " | " + currentState + " | " + nextState)

        # Update approved to current state
        prev_approval = self.env['depa_welfare_approval_lines'].search([
            ('depa_welfare_approval_lines_id', '=', self.welfare_id.id),
            ('process_setting_id.state.code', '=', prevState)
        ], limit=1)

        prev_approval.write({
            'remark': self.remark,
            'on_date': self.create_date,
            'status': 'approved'
        })

        # Save to approval history lines
        approval_history = {
            "approval_lines_id": prev_approval.id,
            "remark_history": self.remark,
            "on_date_history": self.create_date,
            "status_history": 'approved'
        }
        self.env['depa_welfare_approval_lines_history'].create(approval_history)

        # Update pending to next state
        current_approval = self.env['depa_welfare_approval_lines'].search([
            ('depa_welfare_approval_lines_id', '=', self.welfare_id.id),
            ('process_setting_id.state.code', '=', currentState)
        ], limit=1)

        current_approval.write({
            'remark': '',
            'on_date': False,
            'status': 'pending'
        })

        self.welfare_id.next_state = prevState
        self.welfare_id.state = currentState
        self.welfare_id.prev_state = nextState
        self.welfare_id.state_approval = current_approval.process_approval.id

        self.welfare_id.message_post(body="สวัสดิการเลือกอิสระของคุณถูกอนุมัติแล้ว โดย " + str(prev_approval.process_approval.name) + ".")

        if currentState == 'completed':
            # print(currentState)
            # Start FIN 201 and change to completed state
            fin_no = self.welfare_id.fin_no

            fin100 = self.env['fw_pfb_fin_system_100'].search([
                ('id', '=', fin_no.id),
                ('state', '=', 'completed')
            ], limit=1)

            # print(fin100)

            if fin100:
                employee = self.env['hr.employee'].search([
                    ('user_id', '=', self.welfare_id.welfare_owner.id)
                ], limit=1)

                # last_approval = self.env['hr.employee'].search([
                #     ('id', '=', approval_id)
                # ], limit=1)

                fin100line_domain = [
                    ('fin_id', '=', fin_no.id),
                    ('is_fin_line_welfare_gbdi', '=', False)
                ]
                if employee.department_id.is_gbdi:
                    fin100line_domain = [
                        ('fin_id', '=', fin_no.id),
                        ('is_fin_line_welfare_gbdi', '=', True)
                    ]

                fin100line = self.env['fw_pfb_fin_system_100_line'].search(
                    fin100line_domain,
                limit = 1)

                if fin100line:
                    data = {
                        "requester" : employee.id,
                        "objective": "ขออนุมัติเบิกค่าใช้จ่ายสวัสดิการอิสระ",
                        "priority": "1_normal",
                        "is_welfare": True,
                        "depa_welfare_id": self.welfare_id.id,
                        "fin_lines": [
                            (
                                0,
                                0,
                                {
                                    'fin100_number': fin100.id,
                                    'fin100_line_id': fin100line.id,
                                    'fin_type': fin100.fin_type,
                                    'product_id': fin100line.product_id.id,
                                    'product_uom': fin100line.product_uom.id,
                                    'price_unit': fin100line.price_unit,
                                    'projects_and_plan': fin100line.projects_and_plan.id,
                                    'payment_amount': round(self.welfare_id.amount_total, 2)
                                }
                            )
                        ],
                        "approver": [
                            (
                                0,
                                0,
                                {
                                    'approve_active': True,
                                    'position_index': 1,
                                    'approve_step': 1,
                                    'approve_position': 'DirectorOfOffice',
                                    'employee_id': approval_id,
                                    'fin_position': 'DirectorOfOffice',
                                    'action_date': self.create_date,
                                    'memo': self.remark,
                                    'state':'approve'
                                }
                            )
                        ],
                        'request_amount_total': fin100line.price_unit,
                        'state': 'completed'
                    }
                    self.env['fw_pfb_fin_system_201'].button_trigger()
                    fin201 = self.env['fw_pfb_fin_system_201'].create(data)
                    self.welfare_id.fin201_no = fin201.id

                    fin201.message_post(body="FIN201 ของคุณถูกสร้างและอนุมัติแล้ว")

                    # Update point
                    employee_point = self.env['depa_welfare_hr_lines'].search([
                        ('employee_id', '=', employee.id),
                        ('hr_employee_id.year', '=', self.welfare_id.welfare_fiscal_year.id)
                    ], limit=1)

                    if employee_point:
                        point_remain = round(employee_point.point, 2) - round(self.welfare_id.point_total, 2)
                        employee_point.write({
                            "point": point_remain,
                            "is_sent_point_update": True
                        })

                        # Save to point history lines
                        point_history = {
                            "desc": "ขออนุมัติเบิกค่าใช้จ่ายสวัสดิการอิสระ",
                            "on_date": self.create_date,
                            "point_type": 'minus',
                            "point_usage": round(self.welfare_id.point_total, 2),
                            "point_balance": point_remain,
                            "depa_welfare_id": self.welfare_id.id,
                            "employee_id": employee.id,
                            "welfare_fiscal_year": self.welfare_id.welfare_fiscal_year.id
                        }
                        self.env['point_history_lines'].create(point_history)

                        self.welfare_id.message_post(body="สวัสดิการเลือกอิสระของคุณถเสร็จสมบูรณ์แล้ว")

        return {
            'type': 'ir.actions.act_window_close'
        }
        # raise ValidationError(_('Not your turn'))

    def action_adjustment(self):
        # print(self)
        has_reject_line = False
        for rec in self.welfare_id:
            for line in rec.depa_welfare_lines_ids:
                if line.is_hr_reject:
                    has_reject_line = True
                    break

        if not has_reject_line:
            raise ValidationError(_('การส่งกลับเพื่อแก้ไขจำเป็นต้องมีอย่างน้อย 1 รายการ'))

        approval = self.env['depa_welfare_approval_lines'].search([
            ('depa_welfare_approval_lines_id', '=', self.welfare_id.id),
            ('process_setting_id.state.code', '=', self.welfare_id.state)
        ], limit=1)

        approval.write({
            'remark': self.remark,
            'on_date': self.create_date,
            'status': 'adjust'
        })

        # Save to approval history lines
        approval_history = {
            "approval_lines_id": approval.id,
            "remark_history": self.remark,
            "on_date_history": self.create_date,
            "status_history": 'adjust'
        }
        self.env['depa_welfare_approval_lines_history'].create(approval_history)

        self.welfare_id.next_state = self.welfare_id.state
        self.welfare_id.state = self.welfare_id.prev_state
        self.welfare_id.prev_state = 'draft'
        self.welfare_id.show_button_make_approval = False
        self.welfare_id.state_approval = False

        self.welfare_id.message_post(body="สวัสดิการเลือกอิสระของคุณถูกส่งกลับเพื่อปรับแก้ไขโดยผู้ตวจสอบเอกสารแล้ว")

        return {
            'type': 'ir.actions.act_window_close'
        }
        # raise ValidationError(_('Not your turn'))

    def action_reject(self):
        has_reject_line = False
        for rec in self.welfare_id:
            for line in rec.depa_welfare_lines_ids:
                if line.is_hr_reject:
                    has_reject_line = True
                    break

        if has_reject_line:
            raise ValidationError(_('กรุณาตรวจสอบและกดยกเลิกการแก้ไขในแต่ละรายการก่อนส่งอนุมัติ'))

        approval = self.env['depa_welfare_approval_lines'].search([
            ('depa_welfare_approval_lines_id', '=', self.welfare_id.id),
            ('process_setting_id.state.code', '=', self.welfare_id.state)
        ], limit=1)

        approval.write({
            'remark': self.remark,
            'on_date': self.create_date,
            'status': 'rejected'
        })

        # Save to approval history lines
        approval_history = {
            "approval_lines_id": approval.id,
            "remark_history": self.remark,
            "on_date_history": self.create_date,
            "status_history": 'rejected'
        }
        self.env['depa_welfare_approval_lines_history'].create(approval_history)

        self.welfare_id.next_state = ''
        self.welfare_id.state = 'rejected'
        self.welfare_id.prev_state = ''
        self.welfare_id.show_button_make_approval = False
        self.welfare_id.state_approval = False

        self.welfare_id.message_post(body="สวัสดิการเลือกอิสระของคุณถูกปฎิเสธแล้ว")

        return {
            'type': 'ir.actions.act_window_close'
        }


    def action_recheck(self):
        has_reject_line = False
        for rec in self.welfare_id:
            for line in rec.depa_welfare_lines_ids:
                if line.is_hr_reject:
                    has_reject_line = True
                    break

        if has_reject_line:
            raise ValidationError(_('กรุณาตรวจสอบและกดยกเลิกการแก้ไขในแต่ละรายการก่อนส่งอนุมัติ'))

        approval = self.env['depa_welfare_approval_lines'].search([
            ('depa_welfare_approval_lines_id', '=', self.welfare_id.id),
            ('process_setting_id.state.code', '=', self.welfare_id.state)
        ], limit=1)

        approval.write({
            'remark': self.remark,
            'on_date': self.create_date,
            'status': 'rechecked'
        })

        # Save to approval history lines
        approval_history = {
            "approval_lines_id": approval.id,
            "remark_history": self.remark,
            "on_date_history": self.create_date,
            "status_history": 'rechecked'
        }
        self.env['depa_welfare_approval_lines_history'].create(approval_history)

        recheck_state = "DocumentInspector"
        prevState = ""
        currentState = ""
        nextState = ""

        workflow_states = self._get_workflow_state()

        for i, workflow_state in enumerate(workflow_states):
            if workflow_state[0] == recheck_state:
                prevState = workflow_states[i - 1][0]  # Adjust
                currentState = workflow_states[i][0]  # HR
                nextState = workflow_states[i + 1][0]  # HEAD HR
                break

        recheck_approval = self.env['depa_welfare_approval_lines'].search([
            ('depa_welfare_approval_lines_id', '=', self.welfare_id.id),
            ('process_setting_id.state.code', '=', recheck_state)
        ], limit=1)

        self.welfare_id.next_state = nextState
        self.welfare_id.state = currentState
        self.welfare_id.prev_state = prevState
        self.welfare_id.show_button_make_approval = True
        self.welfare_id.state_approval = recheck_approval.process_approval.id

        self.welfare_id.message_post(body="สวัสดิการเลือกอิสระของคุณมีการส่งให้ตรวจสอบเอกสารอีกครั้ง")

        return {
            'type': 'ir.actions.act_window_close'
        }