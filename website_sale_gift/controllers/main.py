# -*- coding: utf-8 -*-
import openerp
from openerp import SUPERUSER_ID
from openerp import http
from openerp.http import request
from openerp.tools.translate import _


class website_sale_voucher(openerp.addons.website_sale.controllers.main.website_sale):

    @http.route(['/shop/pricelist'], type='http', auth="public", website=True)
    def pricelist(self, promo, **post):
        cr, uid, context, model = request.cr, request.uid, request.context, request.registry
        uid = uid

        # If the code used is one product.gift, we check : validity and is ok, we create a new line in the cart with the amount.
        pg = model['product.gift'].search(cr, SUPERUSER_ID, [('code', '=', promo)], context=context)
        if len(pg):
            pg = model['product.gift'].browse(cr, SUPERUSER_ID, pg, context=context)[0]
            if pg.is_used:
                resp = request.redirect("/shop/cart?gift_msg=%s" % _("This code has been already used !"))
            elif pg.is_expired():
                resp = request.redirect("/shop/cart?gift_msg=%s" % _("The code is expired"))
            else:
                order = request.website.sale_get_order(force_create=1)
                for ol in order.order_line:
                    if ol.product_id.is_gift and ol.price_unit > 0:
                        return request.redirect("/shop/cart?gift_msg=%s" % _("You can not use gift to buy another gift"))
                    if ol.name == pg.code:
                        return request.redirect("/shop/cart?gift_msg=%s" % _("This code already used in this order"))

                model['sale.order.line'].create(cr, SUPERUSER_ID, {
                    'order_id': order.id,
                    'product_id': request.env.ref('website_sale_gift.voucher_gift').product_variant_ids[0].id,
                    'product_uom_qty': 1,
                    'price_unit': pg.amount*-1,
                    'name': pg.code
                }, context=context)
                resp = request.redirect("/shop/cart?ok")

        # else we fallback on default pricelist code
        else:
            resp = super(website_sale_voucher, self).pricelist(promo, **post)
        return resp

    # Call in ajax to check price when update qty via +/-
    # Useless by defaut since quantity widget is removed when product is a gift !
    @http.route(['/shop/get_unit_price'], type='json', auth="public", methods=['POST'], website=True)
    def get_unit_price(self, product_ids, add_qty, use_order_pricelist=False, **kw):
        cr, pool = request.cr, request.registry
        price = {}
        so = pool['sale.order'].browse(cr, SUPERUSER_ID, request.session['sale_order_id'])

        if so.using_gift_cart:
            for ol in so.order_line:
                if ol.product_id.is_gift:
                    price[ol.product_id.id] = ol.price_unit

        resp = super(website_sale_voucher, self).get_unit_price(product_ids, add_qty, use_order_pricelist=False, **kw)

        if so.using_gift_cart:
            for ol in so.order_line:
                if ol.product_id.is_gift:
                    resp[ol.product_id.id] = ol.price_unit
        return resp
