# -*- coding: utf-8 -*-
from odoo import http

# class DepaWelfare(http.Controller):
#     @http.route('/depa_welfare/depa_welfare/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/depa_welfare/depa_welfare/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('depa_welfare.listing', {
#             'root': '/depa_welfare/depa_welfare',
#             'objects': http.request.env['depa_welfare.depa_welfare'].search([]),
#         })

#     @http.route('/depa_welfare/depa_welfare/objects/<model("depa_welfare.depa_welfare"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('depa_welfare.object', {
#             'object': obj
#         })