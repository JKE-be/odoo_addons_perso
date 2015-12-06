import openerp
from openerp.tests.common import TransactionCase
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.tools.misc import DEFAULT_SERVER_DATE_FORMAT


class TestCart(TransactionCase):

    def setUp(self):
        super(TestCart, self).setUp()
        self.order = self.registry('sale.order')
        self.order_line = self.registry('sale.order.line')
        self.gift = self.registry('product.gift')

        self.gift_product = self.env.ref('website_sale_gift.voucher_gift_25').product_variant_ids[0]
        self.gift_product_use = self.env.ref('website_sale_gift.voucher_gift').product_variant_ids[0]

    def test_creation_code(self):
        cr, uid = self.cr, self.uid

        gift_number = self.gift.search_count(cr, uid, [])
        sale_order = self.order.create(cr, uid, {'partner_id': self.env.ref('base.res_partner_2').id})
        self.order_line.create(cr, uid, {
            'order_id': sale_order,
            'product_id': self.gift_product.id,
            'product_uom_qty': 1,
            'name': 'New Gift card'
        })
        sale_order = self.order.browse(cr, uid, sale_order)
        sale_order.action_button_confirm()
        inv_id = sale_order.action_invoice_create()
        inv = self.env['account.invoice'].browse(inv_id)
        inv.signal_workflow('invoice_open')
        inv.confirm_paid()

        new_gift_number = self.gift.search_count(cr, uid, [])

        newgift_id = self.gift.search(cr, uid, [], order='id desc', limit=1)
        newgift = self.gift.browse(cr, uid, newgift_id)

        self.assertEquals(new_gift_number, gift_number+1, "Gift code not generated !")
        self.assertEquals(newgift.amount, self.gift_product.list_price, "Gift code amount wrong !")
        self.assertEquals(newgift.is_used, False, "Gift code marked as used !")
        temp = (datetime.now() + relativedelta(years=1) - relativedelta(days=1)).strftime(DEFAULT_SERVER_DATE_FORMAT)
        self.assertTrue(newgift.date_end > temp, "Gift code date error !")

    def test_creation_multi_code(self):
        cr, uid = self.cr, self.uid

        TO_CREATE = 5

        gift_number = self.gift.search_count(cr, uid, [])
        sale_order = self.order.create(cr, uid, {'partner_id': self.env.ref('base.res_partner_2').id})
        self.order_line.create(cr, uid, {
            'order_id': sale_order,
            'product_id': self.gift_product.id,
            'product_uom_qty': TO_CREATE,
            'name': 'New Gift card '
        })
        sale_order = self.order.browse(cr, uid, sale_order)
        sale_order.action_button_confirm()
        inv_id = sale_order.action_invoice_create()
        inv = self.env['account.invoice'].browse(inv_id)
        inv.signal_workflow('invoice_open')
        inv.confirm_paid()

        new_gift_number = self.gift.search_count(cr, uid, [])
        self.assertEquals(new_gift_number, gift_number+TO_CREATE, "All Gift code not generated !")

    def test_use_code(self):
        cr, uid = self.cr, self.uid

        gift_id = self.gift.search(cr, uid, [('is_used', '=', False)], order='id desc', limit=1)
        gift = self.gift.browse(cr, uid, gift_id)
        self.assertFalse(gift.is_used, 'Gift code already consumed')

        sale_order = self.order.create(cr, uid, {'partner_id': self.env.ref('base.res_partner_2').id})
        self.order_line.create(cr, uid, {
            'order_id': sale_order,
            'product_id': self.gift_product_use.id,
            'product_uom_qty': 1,
            'name': gift.code
        })
        sale_order = self.order.browse(cr, uid, sale_order)
        sale_order.action_button_confirm()

        gift.refresh()
        self.assertTrue(gift.is_used, 'Gift code is not consumed')

    def test_use_code_already_used(self):
        cr, uid = self.cr, self.uid
        catched = False

        gift_id = self.gift.search(cr, uid, [('is_used', '=', True)], order='id desc', limit=1)
        gift = self.gift.browse(cr, uid, gift_id)
        self.assertTrue(gift.is_used, 'Gift code not consumed')

        sale_order = self.order.create(cr, uid, {'partner_id': self.env.ref('base.res_partner_2').id})
        self.order_line.create(cr, uid, {
            'order_id': sale_order,
            'product_id': self.gift_product_use.id,
            'product_uom_qty': 1,
            'name': gift.code
        })
        sale_order = self.order.browse(cr, uid, sale_order)

        try:
            sale_order.action_button_confirm()
        except openerp.exceptions.Warning:
            catched = True

        self.assertTrue(catched, 'Code already used should raise a warning')
