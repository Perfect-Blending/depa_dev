# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


import werkzeug
import json
import base64

import odoo.http as http
from odoo.http import request

from odoo import SUPERUSER_ID, _
from odoo.http import request
from datetime import datetime, date
from datetime import datetime, timedelta, time
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.portal.controllers.mail import PortalChatter

class CustomChatter(PortalChatter):

    @http.route(['/mail/chatter_post'], type='http', methods=['POST'], auth='public', website=True)
    def portal_chatter_post(self, res_model, res_id, message, **kw):
        res = super(CustomChatter, self).portal_chatter_post(res_model, res_id, message, **kw)
        msg = request.env['mail.message'].sudo().search([['model','like',res_model],['message_type','=','comment'],['res_id','=',res_id]],order="id desc",limit=1)
        if kw.get('attachment_ids'):
            msg.sudo().write({'attachment_ids':[[0,0,{
                'name':kw['attachment_ids'].filename,
                'datas_fname':kw['attachment_ids'].filename,
                'datas': base64.b64encode(kw['attachment_ids'].read()),
                'res_model': res_model,
                'res_id': res_id,
                }]] })
        return res

class WebsiteMachineRepair(CustomerPortal):

    @http.route('/machine_repair', type="http", auth="public", website=True)
    def machine_repair_request(self, **kw):
        """Let's public and registered user submit a Machine Repair Request"""
        name = ""
        if http.request.env.user.name != "Public user":
            name = http.request.env.user.name
            
        email = http.request.env.user.partner_id.email
        phone = http.request.env.user.partner_id.phone
        values = {'user_ids': name,'email':email,'phone':phone}
        
        return http.request.render('bi_machine_repair_management.bi_create_machine_repair', values)

    @http.route('/machine_repair/thankyou', type="http", auth="public", website=True)
    def machine_repair_thankyou(self, **post):
        """Displays a thank you page after the user submit a Machine Repair Request"""
        
        user_brw = request.env['res.users'].sudo().browse(request._uid)
        technician_obj = request.env['res.users'].sudo().browse(SUPERUSER_ID)
        Attachments = request.env['ir.attachment']
        upload_file = post['upload']
        

        if upload_file:
            data = upload_file.read()
        else:
            return request.redirect("/machine_repair?image_msg=1")
        
        vals = {
                    'name' : post['name'],
                    # 'technician_id' : technician_obj.id,
                    'partner_id' : user_brw.partner_id.id,
                    'client_email' : post['email_from'],
                    'client_phone' : post['phone'],
                    'company_id' : user_brw.company_id.id or False,
                    'repair_request_date' : datetime.now(),
                    'priority' : post['priority'],
                    'product_id' : post['product_id'],
                    'brand' : post['brand'],
                    'model' : post['model'],
                    'color' : post['colors'],
                    'year' : post['year'],
                    'damage' : post['damage'],
                    'machine_brand' : post['brand'],
                    'machine_model' : post['model'],
                    'machine_manufacturing_year' : post['year'],
                    'stage' : "new",
                    'problem' : post['problem'],
                    'machine_services_id' : post['machine_services_id'],
            }

        machine_repair_obj = request.env['machine.repair'].sudo().create(vals)
        
        if upload_file:
            attachment_id = Attachments.sudo().create({
                'name': upload_file.filename,
                'type': 'binary',
                'datas': base64.encodestring(data),
                # 'datas_fname': upload_file.filename,
                'public': True,
                'res_model': 'ir.ui.view',
                'machine_repair_id' : machine_repair_obj.id,
            }) 

        return request.render("bi_machine_repair_management.machine_repair_request_thank_you")  

    def _prepare_portal_layout_values(self):
        values = super(WebsiteMachineRepair, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id

        machine_repair = request.env['machine.repair']
        partner_machine_repair_count = machine_repair.sudo().search([('partner_id','=',partner.id)])
        repair_count = machine_repair.sudo().search_count([('partner_id','=',partner.id)])

        values.update({
            'repair_count': repair_count,
        })
        return values  

    @http.route(['/my/machine_repair', '/my/machine_repair/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_machine_repair(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        machine_repair = request.env['machine.repair']

        domain = []
        archive_groups = self._get_archive_groups('machine.repair', domain)
        # count for pager
        repair_count = machine_repair.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/machine_repair",
            total=repair_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        #supports = support_ticket.search(domain,offset=pager['offset'])
        partner = request.env.user.partner_id
        machine = machine_repair.sudo().search([('partner_id','=',partner.id)])
        request.session['my_ticket_history'] = machine.ids[:100]

        values.update({
            'machine': machine.sudo(),
            'page_name': 'machine_repair',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/machine_repair',
        })
        return request.render("bi_machine_repair_management.portal_my_machine_repair", values) 

    @http.route(['/machine/view/detail/<model("machine.repair"):machine>'],type='http',auth="public",website=True)
    def machine_repair_view(self, machine, category='', search='', **kwargs):
        
        context = dict(request.env.context or {})
        machine_repair_obj = request.env['machine.repair']
        context.update(active_id=machine.id)
        machine_repair_data_list = []
        repair_data = machine_repair_obj.sudo().browse(int(machine))
        
        for items in repair_data:
            machine_repair_data_list.append(items)
            
        return http.request.render('bi_machine_repair_management.machine_repair_request_view',{
            'machine_repair_data_list': machine
        })                            

    @http.route(['/machine_repair/message'],type='http',auth="public",website=True)
    def machine_message(self, **post):
        Attachments = request.env['ir.attachment']
        upload_file = post['upload']
        if upload_file:
            data = upload_file.read()

        #data = base64.encodestring(upload_file.read())
        
        if ',' in post.get('machine_id'):
            bcd = post.get('machine_id').split(',')
        else : 
            bcd = [post.get('machine_id')]
            
        machine_repair_obj = request.env['machine.repair'].sudo().search([('id','=',bcd)]) 
            
        if upload_file:
            attachment_id = Attachments.sudo().create({
                'name': upload_file.filename,
                'type': 'binary',
                'datas': base64.encodestring(data),
                # 'datas_fname': upload_file.filename,
                'public': True,
                'res_model': 'ir.ui.view',
                'machine_repair_id' : machine_repair_obj.id,
            }) 
        
        context = dict(request.env.context or {})
        machine_repair_obj = request.env['machine.repair']
        if post.get( 'message' ):
            message_id1 = request.env['machine.repair'].message_post(
                type='comment',
                subtype='mt_comment') 
                
            message_id1.body = post.get( 'message' )
            message_id1.type = 'comment'
            message_id1.subtype = 'mt_comment'
            message_id1.model = 'machine.repair'
            message_id1.res_id = post.get( 'machine_id' )
                    
        return http.request.render('bi_machine_repair_management.machine_repair_request_thank_you') 
        
    @http.route(['/machine/comment/<model("machine.repair"):machine>'],type='http',auth="public",website=True)
    def machine_comment_page(self, machine,**post):  
        
        return http.request.render('bi_machine_repair_management.machine_repair_comment',{'machine': machine}) 
     
    @http.route(['/machine_repair/comment/send'],type='http',auth="public",website=True)
    def machine_repair_comment(self, **post):
        
        context = dict(request.env.context or {})
        machine_repair_obj = request.env['machine.repair'].browse(int(post['machine_id']))
        machine_repair_obj.update({
                'customer_rating' : post['customer_rating'],            
                'comment' : post['comment'],
        })
        return http.request.render('bi_machine_repair_management.machine_repair_rating_thank_you')
              	
    	       
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:        
