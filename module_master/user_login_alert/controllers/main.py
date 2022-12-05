# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2017-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Niyas Raphy(<https://www.cybrosys.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import datetime
import time

try:
    import httpagentparser
except ImportError:
    pass
from time import gmtime, strftime, localtime
from pytz import timezone
from odoo.addons.web.controllers import main
from odoo.http import request
from odoo.exceptions import Warning
import odoo
import odoo.modules.registry
from odoo.tools.translate import _
from odoo import http


class Home(main.Home):

    @http.route('/web/login', type='http', auth="public")
    def web_login(self, redirect=None, **kw):
        main.ensure_db()
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return http.redirect_with_hash(redirect)

        if not request.uid:
            request.uid = odoo.SUPERUSER_ID

        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None
        if request.httprequest.method == 'POST':
            old_uid = request.uid
            uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
            if uid is not False:
                user_rec = request.env['res.users'].sudo().search([('id', '=', uid)])
                if user_rec.partner_id.email and user_rec.has_group('user_login_alert.receive_login_notification'):
                    send_mail = 0
                    agent = request.httprequest.environ.get('HTTP_USER_AGENT')
                    agent_details = httpagentparser.detect(agent)
                    user_os = agent_details['os']['name']
                    browser_name = agent_details['browser']['name']
                    ip_address = request.httprequest.environ['REMOTE_ADDR']

                    send_mail = 1
                    user_rec.last_logged_ip = ip_address
                    user_rec.last_logged_browser = browser_name
                    user_rec.last_logged_os = user_os

                    # if user_rec.last_logged_ip and user_rec.last_logged_browser and user_rec.last_logged_os:
                    #     if user_rec.last_logged_ip != ip_address or user_rec.last_logged_browser != browser_name or user_rec.last_logged_os != user_os:
                    #         send_mail = 1
                    #         user_rec.last_logged_ip = ip_address
                    #         user_rec.last_logged_browser = browser_name
                    #         user_rec.last_logged_os = user_os
                    #     else:
                    #         send_mail = 0
                    # else:
                    #     send_mail = 1
                    #     user_rec.last_logged_ip = ip_address
                    #     user_rec.last_logged_browser = browser_name
                    #     user_rec.last_logged_os = user_os

                    if send_mail == 1:
                        email_to = user_rec.partner_id.email
                        thailand = timezone('Asia/Bangkok')
                        local_time = datetime.datetime.now(thailand)
                        current_date_time = local_time.strftime("%Y-%m-%d %H:%M:%S")
                        # current_date_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
                        message_body = '<p> เรียน ' + user_rec.name + ' </p> ' + \
                                       '<p> บัญชีของคุณเข้าสู่ระบบเมื่อ : ' + current_date_time + ' </p> ' + \
                                       '<p> IP Address:  ' + ip_address + '</p>' + \
                                        '<p> เบราเซอร์: ' + browser_name + '</p> ' + \
                                        '<p> ระบบปฏิบัติการ: ' + user_os + '</p>'
                        message_body += '*หากท่านไม่ได้เริ่มกระบวนการเข้าสู่ระบบ ขอแนะนำให้เปลี่ยนรหัสผ่านใหม่โดยทันที'
                        template_obj = request.env['mail.mail']
                        template_data = {
                            'subject': 'แจ้งเตือนเข้าสู่ระบบ odoo',
                            'body_html': message_body,
                            'email_from': request.env.user.company_id.email,
                            'email_to': email_to
                        }
                        template_id = template_obj.create(template_data)
                        # template_obj.send(template_id)
                        template_id.send()
                request.params['login_success'] = True
                if not redirect:
                    redirect = '/web'
                return http.redirect_with_hash(redirect)
            request.uid = old_uid
            values['error'] = _("Wrong login/password")
        return request.render('web.login', values)
