# -*- coding: utf-8 -*-
{
    'name':'MRP customization',
    'version':'18.0.0.1',
    'summary':'MRP customization',
    'description':'add cost in to bill of materials.',
    'category':'Manufacturing/Bom',
    'website': 'http://warlocktechnologies.com',
    'author': "Warlock Technologies Pvt Ltd.",
    'depends':['base', 'mrp'],
    'data': [
        'security/ir.model.access.csv',
        'security/security_group.xml',
        'data/mail_template.xml',
        'views/bill_of_material.xml',
        'views/mrp_production_views.xml',
        'wizard/bom_reject_wizard.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'wt_mrp_cost/static/src/xml/bom_overview_table_inherit.xml',
            'wt_mrp_cost/static/src/xml/bom_overview_line_inherit.xml',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3'
}