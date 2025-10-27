# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class MrpProduction(models.Model):
    """ Manufacturing Orders """
    _inherit = 'mrp.production'


    bom_id = fields.Many2one(
        'mrp.bom', 'Bill of Material', readonly=False,
        domain="""[ 
        '&',
            '|',
                ('company_id', '=', False),
                ('company_id', '=', company_id),
            '&',
                '|',
                    ('product_id','=',product_id),
                    '&',
                        ('product_tmpl_id.product_variant_ids','=',product_id),
                        ('product_id','=',False),
        ('type', '=', 'normal'),('state', '=', 'approve')]""",
        check_company=True, compute='_compute_bom_id', store=True, precompute=True,
        help="Bills of Materials, also called recipes, are used to autocomplete components and work order instructions.")
