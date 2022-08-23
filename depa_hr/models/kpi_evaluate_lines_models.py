from odoo import models, fields, api

class kpi_evaluate_lines(models.Model):
    _name = 'kpi_evaluate_lines'
    _description = 'ลำดับการอนุมัติ'
    _order = 'step asc'

    evaluate_line_id = fields.Many2one(
        "kpi_main",
        string="Evaluate line id"
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string="Employee Name"
    )
    job_id_name = fields.Many2one(
        'hr.job',
        string="Job name"
    )
    step = fields.Selection(
        string="Step",
        selection=[
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
            ('4', '4'),
            ('5', '5'),
            ('6', '6'),
            ('7', '7'),
            ('8', '8')
        ],
        default='1'
    )
    status = fields.Selection(
        string="Status",
        selection=[
            ('1', 'ผู้บังคับบัญชาขั้นต้น'),
            ('2', 'ผอ.ฝ่าย'),
            ('3', 'ฝ่ายที่เกี่ยวข้อง-1'),
            ('4', 'เลขา ชสศด./รสศด.'),
            ('5', 'ชสศด.'),
            ('6', 'รสศด.'),
            ('7', 'ฝ่ายที่เกี่ยวข้อง-2'),
            ('8', 'ผสศด.')
        ],
        readonly=True,
        compute='set_step'
    )
    # dummy = fields.Boolean(
    #     string="dummy",
    #     related='employee_id.dummy',
    #     readonly=True
    # )
    # approve_type = fields.Selection(
    #     string="Approve type", selection=[
    #         ('require', 'Is require to approve'),
    #         ('comments', 'Comments only')]
    # )
    evaluate_time = fields.Datetime(
        string='evaluate time',
        copy=False
    )
    comment = fields.Char(
        string='comment',
        copy=False
    )
    evaluate_status = fields.Selection(
        string="status",
        selection=[
            ('0', 'รอประเมิน'),
            ('1', 'ประเมินแล้ว'),
            ('3', 'ส่งกลับแก้ไข')
        ],
        copy=False
    )
    evaluate_setting_id = fields.Many2one(
        'kpi_evaluate_setting',
        string="evaluate id"
    )
    evaluate_ratio = fields.Float(
        string="สัดส่วน",
        digits=(10, 4)
    )
    is_active = fields.Boolean(
        string='Active',
        default=True,
    )
    sequence = fields.Integer(
        string='Sequence',
        index=True
    )

    @api.depends('step')
    # @api.onchange('step')
    def set_step(self):
        # self.ensure_one()
        for record in self:
            if record.step:
                step = record.step
                # record.update({'status':step})
                record.status = step

    @api.onchange('employee_id')
    def employee_id_changed(self):
        self.job_id_name = self.employee_id.job_id