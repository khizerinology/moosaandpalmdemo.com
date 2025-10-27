# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    currency_id = fields.Many2one('res.currency', string='Currency')
    cost = fields.Monetary(string='Cost')
