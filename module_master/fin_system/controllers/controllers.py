# -*- coding: utf-8 -*-
from odoo import http

# class FinSystem(http.Controller):
#     @http.route('/fin_system/fin_system/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fin_system/fin_system/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fin_system.listing', {
#             'root': '/fin_system/fin_system',
#             'objects': http.request.env['fin_system.fin_system'].search([]),
#         })

#     @http.route('/fin_system/fin_system/objects/<model("fin_system.fin_system"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fin_system.object', {
#             'object': obj
#         })