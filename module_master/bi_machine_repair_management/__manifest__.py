# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Machine Repair Management-All types of Product/Machine in odoo',
    'version': '12.0.0.5',
    'category': 'Industries',
    'summary': 'This module help Machine/Spar-part Repair, Laptop repair/computer Servicing any kind of product Repair management.',
    "description": """


    """,
    'author': 'wattanadev',
    'price': 69,
    'currency': "EUR",
    'website': 'https://www.bionesoft.com',
    'depends': ['base','sale_management','stock','project','account','website','website_sale','document','hr_timesheet'],
    'data': [
                "security/machine_repair_security.xml",
                "security/ir.model.access.csv",
                "views/configuration_view.xml",
                "views/machine_repairs.xml",
                "views/machine_view.xml",
                "report/machine_repair.xml",
                "report/machine_repair_report_view.xml",
                "report/machine_label_report_view.xml",
                "data/mail_template_data.xml",
                "views/setting_view.xml",

                # Website
                #"data/data.xml",
                "views/machine_repair_template.xml",
                
             ],
	'qweb': [
        "static/src/xml/chatter.xml",
		    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    "images":["static/description/Banner.png"],
    'live_test_url':'',
}
