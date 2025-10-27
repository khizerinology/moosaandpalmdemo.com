# -*- coding: utf-8 -*-

from collections import defaultdict, OrderedDict
from datetime import date, datetime, time, timedelta
import json

from odoo import api, fields, models, _
from odoo.tools import float_compare, float_round, format_date, float_is_zero
from odoo.exceptions import UserError

class ReportBomStructure(models.AbstractModel):
    _inherit = 'report.mrp.report_bom_structure'


    @api.model
    def _get_bom_data(
        self, bom, warehouse, product=False, line_qty=False, bom_line=False,
        level=0, parent_bom=False, parent_product=False, index=0, product_info=False,
        ignore_stock=False, simulated_leaves_per_workcenter=False
    ):
        # Call the base method
        bom_report_line = super()._get_bom_data(
            bom, warehouse, product=product, line_qty=line_qty, bom_line=bom_line,
            level=level, parent_bom=parent_bom, parent_product=parent_product,
            index=index, product_info=product_info, ignore_stock=ignore_stock,
            simulated_leaves_per_workcenter=simulated_leaves_per_workcenter
        )

        bom_report_line['cost'] = 0.0
        for line in bom.bom_line_ids:
            line_quantity = (bom_report_line['quantity'] / (bom.product_qty or 1.0)) * line.product_qty
            line_total_cost = line.cost * line_quantity if line.cost else 0.0
            bom_report_line['cost'] += line_total_cost

        return bom_report_line


    @api.model
    def _get_component_data(self, parent_bom, parent_product, warehouse, bom_line, line_quantity, level, index, product_info, ignore_stock=False):
        # Call super to get the original data dict
        result = super()._get_component_data(
            parent_bom, parent_product, warehouse, bom_line,
            line_quantity, level, index, product_info, ignore_stock
        )

        # Compute custom cost from BoM line
        company = parent_bom.company_id or self.env.company
        line_cost = bom_line.cost * line_quantity
        rounded_cost = company.currency_id.round(line_cost)

        # Add custom cost to the result
        result['cost'] = rounded_cost

        return result
