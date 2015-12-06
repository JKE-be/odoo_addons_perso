{
    'name': 'E-commerce gift',
    'category': 'Website',
    'summary': 'Sell and use Gift card in your e-commerce',
    'version': '0.1',
    'description': """
E-commerce gift card
======================

When a customer buy a product marked as a gift.
One the invoice is paid, we generate one gift card and send the code by email to the customer.

This code can be used during 1 year like a 'coupon code' in ecommerce.
        """,
    'author': 'Jeremy Kersten',
    'depends': ['website_sale'],
    'data': [
        'data/data.xml',
        'views/templates.xml',
        'views/views.xml',
        'security/ir.model.access.csv',
        'security/website_sale.xml',
    ],
    'installable': True,
    'application': False,
}
