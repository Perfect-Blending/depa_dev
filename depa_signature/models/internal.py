from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.http import request
# from odoo.add_ons.pfb_saraban.internal import internalDocument
from datetime import timedelta, datetime, date
import logging
from lxml import etree
import json
import base64
from io import BytesIO
from docx import Document
from docx.shared import Inches
import requests as r

_logger = logging.getLogger(__name__)


class internalDocumentInherit(models.Model):
    _inherit = 'document.internal.main'

    doc_pdf_signed = fields.Many2many(
        'ir.attachment',
        "attachment_document_internal_main_signed_rel",
        "document_internal_main_id",
        "attachment_id",
        string='Digital Signature File'
    )
    preview_attachment_id = fields.Many2one(
        'ir.attachment',
        'Preview Attachment'
    )
    head_officer_digital_signed = fields.Boolean(
        default=False,
        copy=False
    )
    file_for_signature = fields.Binary(
        string="D-Signature File",
        copy=False,
        track_visibility='onchange'
    )
    file_name_for_signature = fields.Char(
        string="D-Signature File",
        copy=False,
        track_visibility='onchange'
    )
    template = fields.Html(
        string="Template",
        default="<button class='btn btn-info btn-sm'><a style='color: white' href='https://short.depa.or.th/templateSignature' target='_blank'>ดาวน์โหลดตัวอย่างไฟล์</a></button>",
        required=False,
        copy=True
    )
    suffix = fields.Text(
        copy=True
    )

    circular_letter_check = fields.Boolean(
        string="หนังสือเวียน",
        default=False,
        copy=False
    )

    invitation_lines_ids = fields.One2many(
        'invitation_lines',
        'invitation_lines_id',
        copy=False
    )

    specific_document_no = fields.Char(
        default=False
    )
    
    specific_date = fields.Date(
        default=False
    )


    def action_preview_document(self):
        doc_id = self.id
        convert_status, data_encoded = self.env['make.approval.wizard'].convert_document(
            self.env['saraban_form'].from_data(doc_id)
        )
        if not convert_status:
            raise ValidationError(_('เกิดข้อผิดพลาดในการแสดงตัวอย่างเอกสาร'))

        attach_vals = {
            'name': '%s.pdf' % ('Document Pdf Preview'),
            'datas': data_encoded,
            'datas_fname': '%s.pdf' % ('Document Pdf Preview'),
        }

        attach_id = self.env['ir.attachment'].create(attach_vals)

        if self.preview_attachment_id:
            try:
                self.preview_attachment_id.unlink()
            except:
                pass
        self.write({'preview_attachment_id': attach_id.id})
        return {
            'type': 'ir.actions.act_url',
            'url': 'web/content/%s?download=true' % (attach_id.id),
            'target': 'current',
        }

    def action_download_signed_document(self):
        if len(self.doc_pdf_signed) == 0:
            raise ValidationError(_('เกิดข้อผิดพลาดในการดาวน์โหลดเอกสารลงนาม'))

        doc_signed = self.doc_pdf_signed[0]
        self.env['download_document_signed_logging'].create({
            'signed_attachment_id': doc_signed.id,
            'user_id': self.env.uid,
            'ip_address': request.httprequest.environ['REMOTE_ADDR']
        })
        return {
            'type': 'ir.actions.act_url',
            'url': 'web/content/%s?download=true' % (doc_signed.id),
            'target': 'current',
        }

    def download_preview_pdf(self):
        url = "https://api.depa.or.th/wordtopdf2"
        file_name = "preview_document.docx"
        data_base64 = False
        docx_file = self.file_for_signature
        if docx_file:
            binary_file = base64.b64decode(docx_file)
            action = {"docxFile": (file_name, binary_file)}
            resp = r.post(url, files=action)

            if resp.status_code == 200:
                json_data = json.loads(resp.text)
                # data_base64 = base64.b64decode(json_data['base64'])
                data_base64 = json_data['base64']

                attach_vals = {
                    'name': '%s.pdf' % ('Document Pdf Preview'),
                    'datas': data_base64,
                    'datas_fname': '%s.pdf' % ('Document Pdf Preview'),
                }

                attach_id = self.env['ir.attachment'].create(attach_vals)

                if self.preview_attachment_id:
                    try:
                        self.preview_attachment_id.unlink()
                    except:
                        pass

                self.write({'preview_attachment_id': attach_id.id})

                return {
                    'type': 'ir.actions.act_url',
                    'url': 'web/content/%s?download=true' % (attach_id.id),
                    'target': 'current',
                }
        else:
            raise ValidationError(_("ยังไม่มีการอัพโหลด D-signature File"))

    
    def action_sent_to_supervisor(self):
        res = super(internalDocumentInherit, self).action_sent_to_supervisor()
        if len(self.invitation_lines_ids) > 0 and not self.circular_letter_check:
            raise ValidationError("ในกรณีที่มีรายชื่อแจ้งท้ายตั้งแต่ 1 รายชื่อขึ้นไป\nกรุณาเลือก หนังสือเวียน ก่อนส่งหนังสือ")
        return res

    @api.multi
    def unlink(self):
        if not self.env.user.has_group('depa_signature.group_user_digital_signature_setting'):
            raise ValidationError("ไม่สามารถลบบันทึกข้อความ/หนังสือลงนามนี้ได้")
        return models.Model.unlink(self)

class DownloadDocumentSignedLogging(models.Model):
    _name = 'download_document_signed_logging'

    signed_attachment_id = fields.Many2one(
        'ir.attachment'
    )
    user_id = fields.Many2one(
        'res.users'
    )
    ip_address = fields.Char(
        string='IP Address'
    )


class InvitationList(models.Model):
    _name = 'invitation_lines'

    invitation_name = fields.Char(
        required=True,
        string="ชื่อ/ตำแหน่งผู้แจ้งท้าย"
    )

    invitation_lines_id = fields.Many2one(
        'document.internal_main',
        string='ผู้แจ้งท้าย',
        ondelete='cascade'
    )

    document_pdf_id = fields.Integer(
        default=0,
    )

    # file = fields.Binary(
    #     string="หนังสือเวียน",
    #     copy=False,
    # )
    # file_names = fields.Char(
    #     copy=False,
    # )

    def buttonDownload(self):
        # if self.invitation_lines_id:
        #     if self.invitation_lines_id.state != 'Done':
        if self.document_pdf_id != 0:
            return {
                'type': 'ir.actions.act_url',
                'url': 'web/content/%s?download=true' % (self.document_pdf_id),
                'target': 'current',
            }
        else:
            raise ValidationError(_('ไม่พบการลงนามสำหรับเอกสารเวียนของบุคคลนี้'))
