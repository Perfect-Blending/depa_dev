# -*- coding: utf-8 -*-
import json
import base64
import logging

from odoo import api, fields, models, tools, _
from odoo import http
from odoo.http import request
from datetime import datetime, time

_logger = logging.getLogger(__name__)


class UploadAttachment(http.Controller):

    def find_notification_by_menu(self, menu, models):
        count = 0        
        model_fount = []
        for m in models:
            model_fount.append(m)
        if menu.child_id:
            for child_menu in menu.child_id:
                retun_data = self.find_notification_by_menu(child_menu, model_fount)
                count = count + retun_data[0]
                if retun_data[1]:
                    for rdata in retun_data[1]:
                        if rdata not in model_fount:
                            model_fount.append(rdata)
        elif menu.action.type == 'ir.actions.act_window' and menu.action.res_model not in model_fount:
            
            model_id = request.env['ir.model'].search([("model", "=", menu.action.res_model)])
            model_fount.append(menu.action.res_model)
            if model_id:
                activities = request.env['mail.activity'].search([("res_model_id", "=", model_id.id),                    
                    ("date_deadline", "<=", datetime.now().date())])
                if activities:
                    count = len(activities)
        return (count, model_fount)
    
    @http.route(['/get_badge_count'], type='http', auth='user', website=True)
    def get_badge_count(self,  **post):
        menu_id = post.get("menu_id")
        all_menu = request.env['ir.ui.menu'].search([('id','=',menu_id)])     
        notification_count = self.find_notification_by_menu(all_menu,[])[0]
        return json.dumps({'count': notification_count})


    @http.route(['/get_badge_count_test'], type='http', auth='user', website=True)
    def get_badge_count_test(self,  **post):
        href_link = post.get("href_link",False)
        actions_data=request.env['ir.actions.act_window'].browse(int(href_link[href_link.rfind('=')+1:]))
        action1 = request.env['ir.actions.act_window'].for_xml_id('pfb_saraban', 'internal_waiteing_menu')
        act_id1 = action1['action'].split(".")[2].split(",")[1]
        name=actions_data.name[actions_data.name.rfind('/')+1:]
        action2 = request.env['ir.actions.act_window'].for_xml_id('pfb_saraban', 'receive_waithing_menu')
        act_id2 = action2['action'].split(".")[2].split(",")[1]
        if act_id1 in href_link:
            all_rec = request.env['document.internal.main'].search([
                ('setting_line_ids.status_approve', '=', '0'),
                ('setting_line_ids.employee_id.user_id', '=', request.env.uid),
                ('state', '!=', 'done')])
            cnt_values = len(all_rec)
            return json.dumps({'count': cnt_values,'menu_label':name})

        elif act_id2 in href_link:
            all_rec = request.env['receive.document.main'].search([
                ('setting_line_ids.status_approve', '=', '0'),
                ('setting_line_ids.employee_id.user_id', '=', request.env.uid),
                ('state', '!=', 'done')])
            # cnt_values = sum([1 for ar in all_rec if ar.menu_count_document])
            cnt_values = len(all_rec)
            return json.dumps({'count': cnt_values,'menu_label':name})
        else:
            return json.dumps({'count': 0,'menu_label':name})
        
    @http.route(['/get_badge_count_head'], type='http', auth='user', website=True)
    def get_badge_count_head(self,  **post):
        text = post.get("text",False)
        
        if(text.find("หนังสือภายใน")>0):
            all_rec = request.env['document.internal.main'].search([
                ('setting_line_ids.status_approve', '=', '0'),
                ('setting_line_ids.employee_id.user_id', '=', request.env.uid),
                ('state', '!=', 'done')])
            cnt_values = len(all_rec)
            return json.dumps({'count': cnt_values,'menu_label':"หนังสือภายใน"})
        elif(text.find("หนังสือรับ")>0):
            all_rec = request.env['receive.document.main'].search([
                ('setting_line_ids.status_approve', '=', '0'),
                ('setting_line_ids.employee_id.user_id', '=', request.env.uid),
                ('state', '!=', 'done')])
            # cnt_values = sum([1 for ar in all_rec if ar.menu_count_document])
            cnt_values = len(all_rec)
            return json.dumps({'count': cnt_values,'menu_label':"หนังสือรับ"})
        else:
            return json.dumps({'count': 0,'menu_label':text})
        
        
    @http.route(['/get_data'], type='http', auth='user', cors='*', csrf=False, website=True)
    def get_data_valuessss(self, **post):
        file_name = post.get("file_name", False)
        if file_name:
            # attach = request.env['ir.attachment'].search([("name","ilike",file_name)],order="id desc",limit=1)
            return json.dumps({'attach': file_name, 'message': "message"})
        else:
            return json.dumps({'attach': file_name, 'message': "message"})
