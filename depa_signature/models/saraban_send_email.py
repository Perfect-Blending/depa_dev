from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import smtplib
from email import encoders
# from email.message import Message
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import base64
from datetime import datetime
from pytz import timezone
import re

class SarabanSendEmail(models.Model):
    _name = 'saraban_send_email'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="เรื่อง"
    )
    body = fields.Text(
        string="เนื้อหา"
    )
    attachment_ids = fields.Many2many(
        "ir.attachment",
        "saraban_send_mail_attachment_rel",
        "saraban_send_mail_attachment_id",
        "ir_attachment_id",
        string='ไฟล์แนบ',
    )
    source_email = fields.Char(
        string="ต้นทาง",
        default="saraban@depa.or.th"
    )
    destination_email = fields.Char(
        string="ปลายทาง",
        help="หากต้องการระบุหลายอีเมลกรุณาใส่อีเมลแล้วคั้นด้วยเครื่องหมาย ,",
        # required=True
    )
    cc_email = fields.Char(
        string="สำเนาถึง",
        help="หากต้องการระบุหลายอีเมลกรุณาใส่อีเมลแล้วคั้นด้วยเครื่องหมาย ,",
        # required=True
    )
    sent_time = fields.Datetime(
        string='ส่งอีเมลเมื่อ',
        copy=False
    )
    state = fields.Selection(
        [
            ('draft', 'ฉบับร่าง'),
            ('sent', 'ส่งแล้ว'),
        ],
        default="draft",
        string="สถานะ"
    )
    email_owner_id = fields.Many2one(
        'res.users',
        string='เจ้าของอีเมล',
    )
    real_name = fields.Text()
    sequence_name = fields.Text()

    def checkEmailFormat(self):
        regx = "^([\w+-.%]+@[\w.]+\.[A-Za-z]{2,4},?)+$"
        if self.destination_email:
            if not re.search(regx, self.destination_email):
                raise ValidationError(_('รูปแบบ email ปลายทาง ไม่ถูกต้อง'))
        if self.cc_email:
            if not re.search(regx, self.cc_email):
                raise ValidationError(_('รูปแบบ email สำเนาถึง ไม่ถูกต้อง'))

    def send_email_action(self):
        self.checkEmailFormat()

        if self.state == 'draft':
            smtp_ssl_host = "smtp.gmail.com"
            smtp_ssl_port = 465
            tz = timezone('Asia/Bangkok')
            hasSettings = self.env['depa_signature_setting'].sudo().search([], limit=1)
            if not hasSettings:
                raise ValidationError(_('กรุณาตั้งค่า email สำหรับฉบับร่าง'))

            email_address = hasSettings.email_to_draft
            email_password = base64.b64decode(hasSettings.email_credential.encode('utf-8')).decode('utf-8')

            email_to = self.destination_email

            subject = self.name
            body = self.body

            msg = MIMEMultipart()
            msg['Subject'] = subject
            msg['From'] = email_address
            msg['To'] = email_to

            msgText = MIMEText(body, "html")
            msg.attach(msgText)

            email_to_list = [x.strip() for x in email_to.split(",")]
            email_cc_list = []

            if self.cc_email:
                email_cc = self.cc_email
                msg['Cc'] = email_cc
                email_cc_list = [x.strip() for x in email_cc.split(",")]

            email_to_list.extend(email_cc_list)

            if self.attachment_ids:
                for i, rec in enumerate(self.attachment_ids):

                    payload = MIMEBase('application', 'octate-stream')
                    payload.set_payload(base64.decodebytes(rec.datas))
                    encoders.encode_base64(payload)

                    # add payload header with filename
                    payload.add_header('Content-Disposition', 'attachment', filename=rec.name)
                    msg.attach(payload)

            try:
                server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)
                server.login(email_address, email_password)
                # server.starttls()
                server.sendmail(email_address, email_to_list, msg.as_string())
                server.quit()
            except Exception as e:
                raise ValidationError(_(e))

            self.update({
                'sent_time': datetime.now(),
                'state': 'sent'
            })
            self.message_post(body="<strong>SYSTEM LOG</strong><br/>"
                                   "อีเมลของคุณถูก ส่งออก แล้ว<br/>"
                                   "เมื่อ "+str(datetime.now(tz).strftime("%d/%m/%Y %H:%M:%S")))

    def reset_to_draft(self):
        if self.state == 'sent':
            tz = timezone('Asia/Bangkok')
            self.update({
                'sent_time': False,
                'state': 'draft'
            })
            self.message_post(body="<strong>SYSTEM LOG</strong><br/>"
                                   "อีเมลของคุณถูกปรับเป็น ฉบับร่าง แล้ว<br/>"
                                   "เมื่อ " + str(datetime.now(tz).strftime("%d/%m/%Y %H:%M:%S")))