# -*- coding: utf-8 -*-
import uuid
from openerp import models, fields, api
from dateutil.relativedelta import relativedelta
from openerp.tools.translate import _
from openerp.addons.website.models.website import slug
from openerp.exceptions import Warning
#from datetime import datetime, timedelta


class sale_order(models.Model):
    _inherit = "sale.order"

    @api.multi
    def action_button_confirm(self):
        """
        Confirms order and creates and validates invoice, confirms pickings.
        """

        # check if some line is gift card used, and mark them as consumed
        gift_card = self.env['product.gift']
        for ol in self.order_line:
            if ol.product_id.is_gift and ol.price_unit < 0:
                # check that gift not already used
                pg = self.env['product.gift'].sudo().search([('code', '=', ol.name)])
                if pg.is_expired():
                    raise Warning(_('This gift card is expired. Please extends it before to valid this order.'))
                if pg.is_used:
                    raise Warning(_('This gift card has been already used. Please fix the issue before to valid this order.'))
                else:
                    gift_card += pg
        gift_card.write({'is_used': True})

        # continue default process
        return super(sale_order, self).action_button_confirm()

    @api.multi
    def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, **kwargs):
        line = self.env['sale.order.line'].browse(line_id)
        p = self.env['product.product'].browse(product_id)
        price = False

        use_gift = self.env.ref('website_sale_gift.voucher_gift')

        if p == use_gift:
            # Force qty gift to 1
            if (add_qty is None and set_qty == 0):
                set_qty = 0
            else:
                set_qty = 1
            add_qty = None
            price = line.price_unit
        else:
            # If a new gift card is added, we remove the use_gift
            if p.is_gift and self.using_gift_cart():
                super(sale_order, self)._cart_update(use_gift.id, add_qty=None, set_qty=0)

        values = super(sale_order, self)._cart_update(product_id, line_id, add_qty, set_qty, **kwargs)

        # restore price if gift card (price has been recomputed with default price by onchange)
        if price and set_qty != 0:
            line.price_unit = price

        return values

    @api.one
    def has_gift_cart(self):
        use_gift = self.env.ref('website_sale_gift.voucher_gift')
        for l in self.order_line:
            if l.product_id.is_gift and l.product_id != use_gift:
                return True
        return False

    @api.one
    def using_gift_cart(self):
        use_gift = self.env.ref('website_sale_gift.voucher_gift')
        for l in self.order_line:
            if l.product_id.is_gift and l.product_id == use_gift:
                return True
        return False


class account_invoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def confirm_paid(self):
        res = super(account_invoice, self).confirm_paid()

        if 'refund' not in self.journal_id.type:
            for il in self.invoice_line:
                if il.product_id.is_gift:
                    for dummy in range(0, int(il.quantity)):
                        name = _('Gift of %s by %s') % (il.price_unit, self.partner_id.name)
                        gift = self.env['product.gift'].create({
                            'name': name,
                            'amount': il.price_unit,
                        })
                        #TODO: use template
                        self.message_post(body='%s: %s' % (name, gift.code))
        return res


class product_template(models.Model):
    _inherit = "product.template"
    is_gift = fields.Boolean('Is Gift')


class product_gift(models.Model):
    _name = "product.gift"

    def _generate(self):
        strformat = self.env['res.users'].browse(self.env.uid).company_id.gift_format
        code = strformat.format(code=str(uuid.uuid4()))
        if self.search_count([('code', '=', code)]) > 0:
            code = self._generate()
        return code

    name = fields.Char('Name')
    code = fields.Char('Code', default=_generate)
    note = fields.Text('Note')
    amount = fields.Float('Amount')
    #TODO manage currency
    date_end = fields.Date('End', default=lambda self: fields.datetime.now() + relativedelta(years=1))
    is_used = fields.Boolean('Used', default=False)

    def is_expired(self):
        return self.date_end < fields.Datetime.now()


class res_company(models.Model):
    _inherit = 'res.company'

    gift_format = fields.Char('Gift format', default=lambda x: '%s{code:.18}' % (x and slug(x.name)+"-" or ''))
