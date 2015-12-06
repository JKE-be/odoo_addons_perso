e-Commerce gift card
=======================

### How it works

When a customer buy a product marked as a gift.
One the invoice is paid, we generate one gift card and send the code by email to the customer.

This code can be used during 1 year like a 'coupon code' in ecommerce.


### New Model

##### product.gift
- name: just for information display in list
- code: the code used in coupon code field
- note: just for information display in form only
- amount: amount of the gift card
- date_end: expired date
- is_used: if this voucher has been already used in a order 'confirmed'


### Model update

##### res.company
- gift_format: New field to specify the format.
   > Eg: `SIX60-{code:.16}`, `{code}`

##### product.product:
- is_gift: 'Is a gift' checkbox


### Data created
1 product: Gift Card
 : This product is used when a user use a coupon code

3 products Gift card [value]
 : Three sample products which will be displayed on website.
That will allow customer to buy a gift card (value: 10, 25, 50)

### Know issue / TODO
 - If invoice has refund, the created codes are not cancelled.
 - Currency is not managed
 - Make expired date delay has a variable
 - Allow to customize mail template
 - Test with a'Tour' from ecommerce

