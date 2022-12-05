# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class MailTemplate(models.Model):
    _inherit = "mail.template"

#     @api.multi
#     def generate_email(self, res_ids, fields=None):
#         '''Method to generate email'''
#         ret = super(MailTemplate, self).generate_email(res_ids, fields=fields)
#  
#         if (self._context.get('body_html', False) or
#                 self._context.get('subject', False) or
#                 self._context.get('email_to', False)):
#             ret['body_html'] = self._context['body_text']
#             ret['subject'] = self._context['subject']
#             ret['email_to'] = self._context['email_to']
#             return ret
#         else:
#             return ret


class SendMail(models.TransientModel):
    _name = "send.email"
    _description = "Send Mail"

    note = fields.Text('Text')

    @api.multi
    def send_email(self):
        '''Method to send email'''
        # self.env['document.internal.main']
        all_employee=self.env['hr.employee'].search([('active', '=', True)])
        _logger.info('all employee email')
        employees=[]
        for employee in all_employee: 
            _logger.info(employee.work_email)
            _logger.info(employee.user_id.name)
            employees.append(employee)
        # list_document=self.env['document.internal.main.setting.line'].search([('status_approve', '=', '0'),('employee_id','=',empoloyees[0].user_id.id)])
        # list_document=self.env['document.internal.main.setting.line'].search([('status_approve', '=', '0')])
        for employee in employees:
            list_internal_document=self.env['document.internal.main.setting.line'].search([('status_approve', '=', '0'),('employee_id','=',employee.id)])
            list_receive_document=self.env['receive.document.main.setting.lines'].search([('status_approve', '=', '0'),('employee_id','=',employee.id)])
            _logger.info(employee.name)
            _logger.info('จำนวนเอกสาร หนังสือภายใน')
            _logger.info(len(list_internal_document))
            _logger.info('จำนวนเอกสาร หนังสือรับ')
            _logger.info(len(list_receive_document))
            if len(list_receive_document) > 0 or len(list_internal_document) > 0:
                _logger.info("Sent mail")
                body = 'Dear ' + employee.name + '\n' + '<br>' + 'หนังสือภายใน <br>' + str(len(list_internal_document))+ '<br>หนังสือรับ <br>' + str(len(list_receive_document))
                email_template_obj = self.env['mail.template']
                email_to = employee.work_email
                template_id = self.env['ir.model.data'].get_object_reference('pfb_saraban','email_template_document_internal_main')[1]
                _logger.info(template_id)
                template_browse = self.env['mail.template'].sudo().browse(template_id)
                
                if template_browse:
                    mail_values = {}
                    mail_values['email_to'] = email_to
                    mail_values['res_id'] = False
                    mail_values['subject'] = 'รอดำเนินการ สารบรรณ'
                    html_content = template_browse.body_html
                    html_content = html_content.replace('Status Approve', str(len(list_internal_document)))
                    # display the application number in email
                    mail_values['body_html'] = body
                    if not mail_values['email_to'] and not mail_values['email_from']:
                        pass
                    mail_mail_obj = self.env['mail.mail']
                    msg_id = mail_mail_obj.sudo().create(mail_values)
                    if msg_id:
                        mail_mail_obj.send(msg_id)
                        _logger.info("Sent1")
                    _logger.info("Sent2")
                _logger.info("Sent3")
        
        # print(self._context.get('active_id'))
        # print(self.note)
#         doc_internal_obj = self.env['document.internal.main'].search([('id','=',self._context.get('active_id'))])
#         rec = doc_internal_obj.setting_line_ids
#         statements = rec.filtered(lambda r: r.status_approve == 0)
#         documents = len(statements)
#         user_id = doc_internal_obj.department_id.member_ids.user_id
#         body = 'Dear ' + user_id.name + '\n' + '\n' + 'Here there are ' + str(documents) + ' Document is waiting for Draft State.'
       
#         email_template_obj = self.env['mail.template']
#         mail_template = email_template_obj.search([('model', '=','document.internal.main')],limit=1)

#         if mail_template:
#             template_id = self.env['ir.model.data'].get_object_reference('pfb_saraban',
#                                                                             'email_template_document_internal_main')[1]
#             template_browse = self.env['mail.template'].sudo().browse(template_id)
# #             email_to = 'janakirgcet@gmail.com'
#             email_to = user_id.email
#             if template_browse:
#                 mail_values = {}
#                 mail_values['email_to'] = email_to
#                 mail_values['res_id'] = False
#                 mail_values['subject'] = 'Document Approval'
#                 html_content = template_browse.body_html
#                 html_content = html_content.replace('Status Approve', str(documents))
#                 # display the application number in email
#                 mail_values['body_html'] = body
#                 if not mail_values['email_to'] and not mail_values['email_from']:
#                     pass
#                 mail_mail_obj = self.env['mail.mail']
#                 msg_id = mail_mail_obj.sudo().create(mail_values)
#                 if msg_id:
#                     mail_mail_obj.send(msg_id)
        
        
