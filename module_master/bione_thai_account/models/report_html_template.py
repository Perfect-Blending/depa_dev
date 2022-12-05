# -*- coding: utf-8 -*-
import time

from odoo.addons.bione_thai_account.models.num2word import num2word
from odoo.osv import expression



import babel
import base64
import copy
import datetime
import dateutil.relativedelta as relativedelta
import logging

import functools
import lxml
from werkzeug import urls

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError
from odoo.tools import pycompat

_logger = logging.getLogger(__name__)


def format_amount(env, amount, currency):
    fmt = "%.{0}f".format(currency.decimal_places)
    lang = env['res.lang']._lang_get(env.context.get('lang') or 'en_US')

    formatted_amount = lang.format(fmt, currency.round(amount), grouping=True, monetary=True)\
        .replace(r' ', u'\N{NO-BREAK SPACE}').replace(r'-', u'\u2011')

    pre = post = u''
    if currency.position == 'before':
        pre = u'{symbol}\N{NO-BREAK SPACE}'.format(symbol=currency.symbol or '')
    else:
        post = u'\N{NO-BREAK SPACE}{symbol}'.format(symbol=currency.symbol or '')

    return u'{pre}{0}{post}'.format(formatted_amount, pre=pre, post=post)




class ReportHtmlTemplate(models.Model):
    _name = 'report.html.template'
    


    def _get_amount_word(self):
        txt = ''
        for obj in self:
            txt = num2word(obj.amount_inv,l='th_TH')
        return txt


    report_header = fields.Char(string = "หัวเอกสาร")
    edit_title = fields.Char(string = "ส่วนราชการ")
    edit_at = fields.Char(string = "ที่",default="")
    edit_story = fields.Char(string = "หัวข้อเรื่อง",default="")
    edit_to = fields.Char(string = "เรียน",default="")
    edit_detail = fields.Html(string = "รายละเอียด")
    thai_date_fix = fields.Char(string = "วันที่")
    name = fields.Char(string = "ชื่อเอกสาร")
    code = fields.Char(string = "รหัสเอกสาร")
    logo = fields.Binary("Logo", attachment=True,help="This field holds the image used as logo for the brand, limited to 400x400px.")

    edit_story2 = fields.Char(string = "หัวข้อเรื่อง")
    edit_to2 = fields.Char(string = "เรียน")
    edit_detail2 = fields.Html(string = "รายละเอียด")

    @api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for doc in self:
            name = doc.code + ' ' + doc.name
            result.append((doc.id, name))
        return result


    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        accounts = self.search(domain + args, limit=limit)
        return accounts.name_get()



    @api.model
    def create(self, vals):
        tools.image_resize_images(vals)
        return super(ReportHtmlTemplate, self).create(vals)