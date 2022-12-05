# -*- coding: utf-8 -*-
{
    'name': 'Sales, Purchase, Warehouse and Accounting Edit Sequence Number',
    
    'author' : 'Softhealer Technologies',
    
    'website': 'https://www.softhealer.com',    
    
    "support": "support@softhealer.com",   
        
    'version': '12.0.1',
    
    'category': 'Extra Tools',

    'summary': """ Edit Sequence Number Module, Update Serial Number App, Sale order Change Sequence No,RFQ Correct Sequence Number, Purchase Order Setup Sequence Number, Invoice Write Over Sequence No, Debit Note Manage Sequence No

""",

    'description': """ Currently, in odoo, you can not edit the sequence number of sales, purchase, warehouse and accounting staff. This module helps the user to edit the sequence number in sales purchase and accounting (invoice bills credit debit notes.).
 Set Sequence Number - Sales, Purchase, Account, Warehouse Odoo
Edit Sequence Number Module, Update Serial Number, Modify sequence number in quotation, Change Sequence No In Sale order, Edit Sequence Number In RFQ, Correct Sequence Number In Purchase Order, Set Up Sequence No In Invoice, Write Over Sequence No In Debit Note,Manage Sequence No In Bill, Arrange Sequence No In Credit note Odoo, Adjust Sequence Number In Request For Quotation, Edit Sequence Number In Po, Replace Sequence No In SO Odoo.
 Edit Sequence Number Module, Update Serial Number App, Quotation Modify sequence Number, Sale order Change Sequence No,RFQ Correct Sequence Number, Purchase Order Setup Sequence Number, Invoice Write Over Sequence No, Debit Note Manage Sequence No,Bill Arrange Sequence No, Credit Note Adjust Sequence No,Request For Quotation Replace Sequence No,PO Edit Sequence Number, SO Update Sequence No Odoo.

""",
    
    'depends': ['sale_management','purchase','account','stock'],
    
    
    'data': [
            'data/edit_sequence.xml',
            'views/sale_order.xml',
            'views/purchase_order.xml',
            'views/account_invoice.xml',
            'views/stock_picking.xml',
            ],
    
    'images': ['static/description/background.png',],              
    
    'auto_install': False,
    'installable' : True,
    'application': True,    
    
    "price": 20,
    "currency": "EUR"        
}
