# models/vendor_category.py
from odoo import models, fields

class VendorCategory(models.Model):
    _name = 'vendor.category'
    _description = 'Vendor Category'

    name = fields.Char(string='Description', required=True, store=True)
    code = fields.Char(string='Code', required=True, store=True)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    vendor_category_id = fields.Many2one(
        'vendor.category',
        string='Vendor Category'
    )


class ProductCategory(models.Model):
    _inherit = 'product.category'

    category_code = fields.Char(string='Code', store=True)
