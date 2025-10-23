# -*- coding: utf-8 -*-
import base64
import csv
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ImportBomWizard(models.TransientModel):
    _name = "import.bom"
    _description = "Import Bill of Materials"

    file_path = fields.Binary(string="Upload CSV", required=True)
    bom_type = fields.Selection([('normal', 'Manufacture'), ('phantom', 'Kit')], required=True, default='normal')

    # -*- coding: utf-8 -*-
import base64
import csv
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ImportBomWizard(models.TransientModel):
    _name = "import.bom"
    _description = "Import Bill of Materials"

    file_path = fields.Binary(string="Upload CSV", required=True)
    bom_type = fields.Selection([('normal', 'Manufacture'), ('phantom', 'Kit')], required=True, default='normal')

    def import_bom_data(self):
        if not self.file_path:
            raise UserError(_("Please upload a CSV file."))

        decoded_file = base64.b64decode(self.file_path)
        lines = decoded_file.decode('utf-8').splitlines()
        reader = csv.DictReader(lines)

        bom_data_map = {}
        bom_header_map = {}
        missing_products = []  # collect missing ingredients

        for row in reader:
            bom_code = row.get('Code', '').strip()
            recipe_name = row.get('Recipe Name', '').strip()
            ingredient_code = row.get('Ingredient Code', '').strip()
            ingredient_name = row.get('Ingredient Name', '').strip()
            quantity = row.get('Quantity', '0').strip()
            uom_name = row.get('Unit', '').strip()
            cost_per_unit = row.get('Cost Per Unit', '0').strip()
            produce_qty = row.get('Produced Quantity', '0').strip()
            produce_uom = row.get('Produced UOM', '').strip()

            if not recipe_name or not ingredient_code or not quantity or not bom_code:
                _logger.warning(f"Skipping incomplete row: {row}")
                continue

            try:
                quantity = float(quantity)
            except ValueError:
                _logger.warning(f"Invalid number in row: {row}")
                continue

            key = (recipe_name, bom_code)
            if key not in bom_data_map:
                bom_data_map[key] = []
                bom_header_map[key] = {
                    'produce_qty': produce_qty,
                    'produce_uom': produce_uom,
                }

            bom_data_map[key].append({
                'ingredient_code': ingredient_code,
                'ingredient_name': ingredient_name,
                'quantity': quantity,
                'uom_name': uom_name,
                'cost': cost_per_unit,
            })

        for (recipe_name, bom_code), lines in bom_data_map.items():
            product_tmpl = self.env['product.template'].search([('name', '=', recipe_name)], limit=1)
            if not product_tmpl:
                product_tmpl = self.env['product.template'].create({'name': recipe_name})

            header_vals = bom_header_map.get((recipe_name, bom_code), {})
            produce_qty = float(header_vals.get('produce_qty') or 0.0)
            produce_uom_name = header_vals.get('produce_uom') or False

            uom_rec = False
            if produce_uom_name:
                uom_rec = self.env['uom.uom'].search([('name', 'ilike', produce_uom_name)], limit=1)

            bom_vals = {
                'product_tmpl_id': product_tmpl.id,
                'type': self.bom_type,
                'product_id': product_tmpl.product_variant_id.id,
                'code': bom_code,
                'state': 'approve',
            }
            if produce_qty:
                bom_vals['product_qty'] = produce_qty
            if uom_rec:
                bom_vals['product_uom_id'] = uom_rec.id

            bom = self.env['mrp.bom'].search([
                ('product_tmpl_id', '=', product_tmpl.id),
                ('type', '=', self.bom_type),
                ('code', '=', bom_code),
            ], limit=1)

            if not bom:
                bom = self.env['mrp.bom'].create(bom_vals)
            else:
                bom.write(bom_vals)

            for line in lines:
                ingredient_code = line['ingredient_code']
                ingredient_name = line['ingredient_name'] or ingredient_code

                # Find ingredient product
                product = self.env['product.product'].search([('default_code', '=', ingredient_code)], limit=1)
                if not product:
                    missing_products.append({
                        'code': ingredient_code,
                        'name': ingredient_name,
                    })
                    continue  # Skip this line for now

                # Find UOM (only search, don't create)
                uom = False
                if line['uom_name']:
                    uom = self.env['uom.uom'].search([('name', 'ilike', line['uom_name'])], limit=1)
                if not uom:
                    _logger.warning(f"UOM not found: {line['uom_name']}, skipping line.")
                    continue

                # Update or create BOM line
                existing_line = bom.bom_line_ids.filtered(lambda l: l.product_id.default_code == ingredient_code)
                if existing_line:
                    existing_line.write({
                        'product_qty': line['quantity'],
                        'product_uom_id': uom.id,
                        'cost': line['cost'],
                    })
                else:
                    bom.write({
                        'bom_line_ids': [(0, 0, {
                            'product_id': product.id,
                            'product_qty': line['quantity'],
                            'product_uom_id': uom.id,
                            'cost': line['cost'],
                        })]
                    })

        # 🔴 At the end, show missing products if any
        if missing_products:
            missing_text = "\n".join([f"{mp['code']} - {mp['name']}" for mp in missing_products])
            _logger.warning(_("RRRRRRRRRRRR----The following ingredient products are missing:\n\n%s") % missing_text)


    # def import_bom_data(self):
    #     if not self.file_path:
    #         raise UserError(_("Please upload a CSV file."))

    #     decoded_file = base64.b64decode(self.file_path)
    #     lines = decoded_file.decode('utf-8').splitlines()
    #     reader = csv.DictReader(lines)

    #     bom_data_map = {}

    #     for row in reader:
    #         bom_code = row.get('Code', '').strip()
    #         recipe_name = row.get('Recipe Name', '').strip()
    #         ingredient_code = row.get('Ingredient Code', '').strip()
    #         ingredient_name = row.get('Ingredient Name', '').strip()
    #         quantity = row.get('Quantity', '0').strip()
    #         uom_name = row.get('Unit', '').strip()
    #         cost_per_unit = row.get('Cost Per Unit', '0').strip()
    #         produce_qty = row.get('Produced Quantity', '0').strip()
    #         produce_uom = row.get('Produced UOM', '').strip()

    #         if not recipe_name or not ingredient_code or not quantity or not bom_code:
    #             _logger.warning(f"Skipping incomplete row: {row}")
    #             continue

    #         try:
    #             quantity = float(quantity)
    #             # cost_per_unit = float(cost_per_unit) if cost_per_unit else 0.0
    #         except ValueError:
    #             _logger.warning(f"Invalid number in row: {row}")
    #             continue

    #         key = (recipe_name, bom_code)
    #         if key not in bom_data_map:
    #             bom_data_map[key] = []
    #         bom_data_map[key].append({
    #             'ingredient_code': ingredient_code,
    #             'quantity': quantity,
    #             'uom_name': uom_name,
    #             'cost': cost_per_unit,
    #         })

    #     for (recipe_name, bom_code), lines in bom_data_map.items():
    #         product_tmpl = self.env['product.template'].search([('name', '=', recipe_name)], limit=1)
    #         if not product_tmpl:
    #             product_tmpl = self.env['product.template'].create({'name': recipe_name})
    #         bom = self.env['mrp.bom'].search([
    #             ('product_tmpl_id', '=', product_tmpl.id),
    #             ('type', '=', self.bom_type),
    #             ('code', '=', bom_code),
    #         ], limit=1)

    #         if not bom:
    #             bom = self.env['mrp.bom'].create({
    #                 'product_tmpl_id': product_tmpl.id,
    #                 'type': self.bom_type,
    #                 'product_id': product_tmpl.product_variant_id.id,
    #                 'code': bom_code,
    #                 'state': 'approve',
    #             })
    #         else:
    #             bom.write({'state': 'approve'})


    #         for line in lines:
    #             product = self.env['product.product'].search([('default_code', '=', line['ingredient_code'])], limit=1)
    #             if not product:
    #                 _logger.warning(f"Ingredient not found: {line['ingredient_code']}")
    #                 continue

    #             uom = self.env['uom.uom'].search([('name', '=', line['uom_name'])], limit=1)
    #             if not uom:
    #                 category = self.env['uom.category'].search([('name', '=', 'Unit')], limit=1)
    #                 if not category:
    #                     category = self.env['uom.category'].create({'name': 'Unit'})

    #                 reference_uom = self.env['uom.uom'].search([
    #                     ('category_id', '=', category.id),
    #                     ('uom_type', '=', 'reference')
    #                 ], limit=1)

    #                 uom = self.env['uom.uom'].create({
    #                     'name': line['uom_name'],
    #                     'category_id': category.id,
    #                     'uom_type': 'bigger' if reference_uom else 'reference',
    #                     'factor': 1.0,
    #                     'rounding': 0.01,
    #                 })

    #             existing_line = bom.bom_line_ids.filtered(lambda l: l.product_id.default_code == line['ingredient_code'])

    #             if existing_line:
    #                 existing_line.write({
    #                     'product_qty': line['quantity'],
    #                     'product_uom_id': uom.id,
    #                     'cost': line['cost'],
    #                 })
    #             else:
    #                 bom.write({
    #                     'bom_line_ids': [(0, 0, {
    #                         'product_id': product.id,
    #                         'product_qty': line['quantity'],
    #                         'product_uom_id': uom.id,
    #                         'cost': line['cost'],
    #                     })]
    #                 })
