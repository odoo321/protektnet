# -*- coding: utf-8 -*-
{
    'name': 'Mail Messages Easy.'
            ' Reply to message, Forward messages or Move messages to other thread, Mark messages,'
            ' Email client style for messages views and more',
    'version': '11.0.1.13',
    'summary': """Read and manage all Odoo messages in one place!""",
    'author': 'Ivan Sokolov',
    'category': 'Social',
    'license': 'GPL-3',
    'website': 'https://demo.promintek.com',
    'description': """
Mail Messages
""",
    'depends': ['base', 'mail'],
    'images': ['static/description/banner.png'],

    'data': [
        'security/groups.xml',
        'views/prt_mail.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}
