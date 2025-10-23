# -*- coding: utf-8 -*-

import csv
import io
import logging
import base64
from odoo import fields, models, api, _

_logger = logging.getLogger(__name__)

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

class StockInventoryLine(models.Model):
    _inherit = 'stock.quant'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id


class ImportProducts(models.TransientModel):
    _name = "import.products"
    _description = "Product Import"
   
    file_path = fields.Binary(type='binary', string="File To Import")

    # def do_import_product_data(self):
    #     if not self.file_path:
    #         raise UserError(_("Please upload a CSV file."))

    #     decoded_file = base64.b64decode(self.file_path)
    #     lines = decoded_file.decode('utf-8').splitlines()
    #     reader = csv.DictReader(lines)

    #     for data in reader:
    #         internal_ref = data.get('Internal Reference', '').strip()
    #         name = data.get('Name', '').strip()
    #         sales_description = data.get('Sales Description', '').strip()
    #         can_be_sold = data.get('Can be sold', '').strip().lower() == 'true'
    #         can_be_purchase = data.get('Can be purchase', '').strip().lower() == 'true'
    #         can_be_POS = data.get('Can be POS', '').strip().lower() == 'true'
    #         sales_price_str = data.get('Sales Price', '').strip()
    #         product_category = data.get('Product Category', '').strip()
    #         product_category_code = data.get('Category Code', '').strip()
    #         primary_vendor_name = data.get('Primary Vendors/Vendor', '').strip()
    #         unit_of_measure_name = data.get('Unit of measure', '').strip()
    #         purchase_uom_name = data.get('Purchase UOM', '').strip()
    #         vendor_price_str = data.get('Primery Vendors/Price', '').strip()
    #         product_type = data.get('Product Type', '').strip()
    #         if not name and not internal_ref and not product_category and not sales_price_str:
    #             continue

    #         category = self.env['product.category'].search([('name', '=', product_category)], limit=1)
    #         cat_vals = {'name': product_category,
    #         'category_code':product_category_code}
    #         if not category:
    #             category = self.env['product.category'].create(cat_vals)
    #         else:
    #             category.write(cat_vals)


    #         # Convert sales price if valid
    #         sales_price = None
    #         cleaned_price = sales_price_str.replace('AED', '').strip()
    #         if cleaned_price:
    #             try:
    #                 sales_price = float(cleaned_price)
    #             except ValueError:
    #                 _logger.warning(f"Invalid Sales Price format: {sales_price_str}")

    #         # Convert vendor price if valid
    #         vendor_price = None
    #         cleaned_vendor_price = vendor_price_str.replace('AED', '').strip()
    #         if cleaned_vendor_price:
    #             try:
    #                 vendor_price = float(cleaned_vendor_price)
    #             except ValueError:
    #                 _logger.warning(f"Invalid Vendor Price format: {vendor_price_str}")


    #         # UOM
    #         uom = None
    #         if unit_of_measure_name:
    #             uom = self.env['uom.uom'].search([
    #                 ('name', 'ilike', unit_of_measure_name)
    #             ], limit=1)

    #         # Purchase UOM
    #         purchase_uom = None
    #         if purchase_uom_name:
    #             purchase_uom = self.env['uom.uom'].search([
    #                 ('name', 'ilike', purchase_uom_name)
    #             ], limit=1)

    #         # Skip if either UOM not found
    #         if not uom or not purchase_uom:
    #             _logger.warning(f"----------Skipping product '{name},----{internal_ref}' due to missing UOM or Purchase UOM.")
    #             continue



    #         # Vendor
    #         vendor = None
    #         if primary_vendor_name:
    #             vendor = self.env['res.partner'].search([
    #                 ('name', '=', primary_vendor_name), ('supplier_rank', '>', 0)
    #             ], limit=1)
    #             # if not vendor:
    #             #     vendor = self.env['res.partner'].create({
    #             #         'name': primary_vendor_name,
    #             #         'supplier_rank': 1
    #             #     })
    #         if product_type == 'Service':
    #             p_type = 'service'

    #         product_vals = {
    #             'default_code': internal_ref or False,
    #             'name': name,
    #             'description_sale': sales_description,
    #             'categ_id': category.id,
    #             'sale_ok': can_be_sold,
    #             'purchase_ok': can_be_purchase,
    #             'available_in_pos': can_be_POS,
    #             'uom_id': uom.id if uom else False,
    #             'uom_po_id': uom.id if uom else False,
    #             # 'uom_po_id': purchase_uom.id if purchase_uom else False,
    #         }

    #         if sales_price is not None:
    #             product_vals['list_price'] = sales_price

    #         # Create or update product
    #         product = self.env['product.template'].search([('default_code', '=', internal_ref)], limit=1)
    #         if product:
    #             product.write(product_vals)
    #             _logger.info(f"Updated product: {internal_ref}")
    #         else:
    #             product = self.env['product.template'].create(product_vals)
    #             _logger.info(f"Created product: {internal_ref or name}")

    #         # Set vendor info only if price is valid
    #         if vendor and can_be_purchase and vendor_price is not None:
    #             self.env['product.supplierinfo'].create({
    #                 'partner_id': vendor.id,
    #                 'product_tmpl_id': product.id,
    #                 'price': vendor_price,
    #                 'product_uomp': purchase_uom.id if purchase_uom else False,
    #                 'min_qty': 1.0,
    #             })

    from odoo.exceptions import UserError

    def do_import_product_data(self):
        if not self.file_path:
            raise UserError(_("Please upload a CSV file."))

        decoded_file = base64.b64decode(self.file_path)
        lines = decoded_file.decode('utf-8').splitlines()
        reader = csv.DictReader(lines)

        skipped_products = [] 

        for data in reader:
            internal_ref = data.get('Internal Reference', '').strip()
            name = data.get('Name', '').strip()
            sales_description = data.get('Sales Description', '').strip()
            can_be_sold = data.get('Can be sold', '').strip().lower() == 'true'
            can_be_purchase = data.get('Can be purchase', '').strip().lower() == 'true'
            can_be_POS = data.get('Can be POS', '').strip().lower() == 'true'
            sales_price_str = data.get('Sales Price', '').strip()
            product_category = data.get('Product Category', '').strip()
            product_category_code = data.get('Category Code', '').strip()
            primary_vendor_name = data.get('Primary Vendors/Vendor', '').strip()
            unit_of_measure_name = data.get('Unit of measure', '').strip()
            purchase_uom_name = data.get('Purchase UOM', '').strip()
            vendor_price_str = data.get('Primery Vendors/Price', '').strip()
            product_type = data.get('Product Type', '').strip()
            inventory_tracking = data.get('Tracking (Unique seriaL number/Lot/no tracking)', '').strip()
            if not name and not internal_ref and not product_category and not sales_price_str:
                continue
            # if name == 'Buffallo Sauce':
                # breakpoint()

            category = self.env['product.category'].search([('name', '=', product_category)], limit=1)
            cat_vals = {'name': product_category, 'category_code': product_category_code}
            if not category:
                category = self.env['product.category'].create(cat_vals)
            else:
                category.write(cat_vals)

            # Convert sales price
            sales_price = None
            cleaned_price = sales_price_str.replace('AED', '').strip()
            if cleaned_price:
                try:
                    sales_price = float(cleaned_price)
                except ValueError:
                    _logger.warning(f"Invalid Sales Price format: {sales_price_str}")

            # Convert vendor price
            vendor_price = None
            cleaned_vendor_price = vendor_price_str.replace('AED', '').strip()
            if cleaned_vendor_price:
                try:
                    vendor_price = float(cleaned_vendor_price)
                except ValueError:
                    _logger.warning(f"Invalid Vendor Price format: {vendor_price_str}")

            # UOM
            uom = None
            # uom = self.env['uom.uom'].search([('name', '=', 'Units')], limit=1)
            if unit_of_measure_name:
                uom = self.env['uom.uom'].search([('name', '=ilike', unit_of_measure_name)], limit=1)

            # Purchase UOM
            purchase_uom = None
            if purchase_uom_name:
                purchase_uom = self.env['uom.uom'].search([('name', '=ilike', purchase_uom_name)], limit=1)

            # Skip if missing UOM
            if not uom:
                skipped_products.append({
                    'code': internal_ref,
                    'name': name,
                    'reason': f"Missing UOM ({unit_of_measure_name}) or Purchase UOM ({purchase_uom_name})"
                })
                continue

            # Vendor
            vendor = None
            if primary_vendor_name:
                vendor = self.env['res.partner'].search([
                    ('name', '=ilike', primary_vendor_name)
                ], limit=1)
                if not vendor:
                    vals={
                    'name': primary_vendor_name,
                    }
                    vendor = self.env['res.partner'].create(vals)

            if product_type == 'Service':
                p_type = 'service'
            product_vals = {
                'default_code': internal_ref or False,
                'name': name,
                'description_sale': sales_description,
                'categ_id': category.id,
                'sale_ok': can_be_sold,
                'purchase_ok': can_be_purchase,
                'available_in_pos': can_be_POS,
                'uom_id': uom.id if uom else False,
                'uom_po_id': uom.id if uom else False,
                'is_storable' : inventory_tracking if inventory_tracking else False
            }

            if sales_price is not None:
                product_vals['list_price'] = sales_price

            product = self.env['product.template'].search([('default_code', '=', internal_ref)], limit=1)
            if product:                
                product.write(product_vals)
                _logger.info(f"Updated product: {internal_ref}")
            else:
                product = self.env['product.template'].create(product_vals)
                _logger.info(f"Created product: {internal_ref or name}")
            # breakpoint()
            # Vendor info
            if vendor and can_be_purchase and vendor_price is not None:
                self.env['product.supplierinfo'].create({
                    'partner_id': vendor.id,
                    'product_tmpl_id': product.id,
                    'price': vendor_price,
                    'product_uomp': purchase_uom.id if purchase_uom else False,
                    'min_qty': 1.0,
                })

        if skipped_products:
            skipped_text = "\n".join([
                f"{sp['code']} - {sp['name']} (Reason: {sp['reason']})"
                for sp in skipped_products
            ])
            _logger.warning(_("The following products were skipped:\n\n%s") % skipped_text)



class OutputOutput(models.TransientModel):
    _name = 'output.output'
    _description = "Bounce file Output"

    file_path = fields.Char('File Location', size=128)
    file = fields.Binary(type='binary', string="Download File", readonly=True)
    flag = fields.Boolean('Flag', default=False)
    note = fields.Text('Note')
