# -*- coding: utf-8 -*-
# Copyright (c) 2019-Present Droggol. (<https://www.droggol.com/>)

{
    'name': 'From SO - Create PO',
    'description': 'From sale order create purchase order and show reserved availability in SO line',
    'summary': 'From sale order create purchase order and show reserved availability in SO line',
    'category': 'Sales/Sales',
    'author': 'Droggol',
    'depends': ['sale_stock', 'purchase'],
    'license': 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'data/mail_template_data.xml',
        'views/dr_so_create_po_templates.xml',
        'views/dr_so_create_po_views.xml',
        'wizard/dr_purchase_order_wizard.xml',
    ],
    # 'assets': {
    #     'web.assets_backend': [
    #         'static/src/xml/dr_reserved_widget.xml',
    #     ]
}
