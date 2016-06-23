# -*- coding: utf-8 -*-
{
    'name': "tty",

    'summary': """
        View tty terminal
    """,

    'description': """
        View tty terminal
    """,

    'author': "Jeremy Kersten",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Administration',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['web'],
    'qweb': [
        "static/src/xml/*.xml",
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
}
