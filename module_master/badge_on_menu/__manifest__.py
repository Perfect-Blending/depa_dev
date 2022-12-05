# -*- coding: utf-8 -*-
#################################################################################
# Author      : CodersFort (<https://codersfort.com/>)
# Copyright(c): 2017-Present CodersFort.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://codersfort.com/>
#################################################################################
{
    "name": "Badge - Menu",
    "summary": "Show Pending Schedule Activity Counter badge on Odoo menu",
    "version": "12.0.10.26",
    "description": """Show Pending Schedule Activity Counter badge on Odoo menu""",
    "version" :  "1.0.0",
    "author": "CodersFort",
    "maintainer": "Ananthu Krishna",
    "website": "http://codersfort.com",
    "images": ["images/Banner.png"],
    "license" :  "Other proprietary",
    "category": "Tools",
    "depends": [
        "base",
        "web",
    ],
    "data": [
        'views/assets.xml',
    ],
    "qweb": ['static/src/xml/menu.xml'],
    "installable": True,
    "application": True,
    "pre_init_hook":  "pre_init_check",
    
}
