# -*- coding: utf-8 -*-
from odoo import http

# class DepaTmi(http.Controller):
#     @http.route('/depa_tmi/depa_tmi/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/depa_tmi/depa_tmi/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('depa_tmi.listing', {
#             'root': '/depa_tmi/depa_tmi',
#             'objects': http.request.env['depa_tmi.depa_tmi'].search([]),
#         })

#     @http.route('/depa_tmi/depa_tmi/objects/<model("depa_tmi.depa_tmi"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('depa_tmi.object', {
#             'object': obj
#         })