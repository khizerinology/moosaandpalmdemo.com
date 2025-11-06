# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################
from odoo import fields, models, api
from odoo.addons.odoo_multi_channel_sale.models.feeds import feed
import copy

auth_url = "https://accounts.salla.sa/oauth2/auth"
token_url = "https://accounts.salla.sa/oauth2/token"


class InheritWkFeed(models.Model):
    _inherit = "wk.feed"

    @api.model
    def get_product_fields(self):
        ProductFields = copy.deepcopy(feed.ProductFields)
        ProductFields.append('salla_product_attribute_options')
        return ProductFields


class ProductVariantFeed(models.Model):
    _inherit = "product.feed"
    salla_product_attribute_options = fields.Char()


class ProductProduct(models.Model):
    _inherit = "product.template"

    # When variant is added in any order then we will require this field value
    # We create a dict to hold the variant id and the options related to that variant
    # we will match these options and assign a variant id to order during import
    # (order data has not variant id but options)
    salla_product_attribute_options = fields.Char()
