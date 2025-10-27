# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.osv.expression import AND, OR
from odoo.exceptions import UserError, ValidationError
from lxml import etree

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval', 'Waiting For Approval'),
        ('approve', 'Approve'),
        ('reject', 'Reject'),
    ], string="Status", default='draft', tracking=True)
    responsible_id = fields.Many2one('res.users', string="Responsible", default=lambda self: self.env.user, readonly=True)
    reject_reason = fields.Text(string="Rejection Reason", tracking=True, readonly=True)

    def action_approve_request(self):
        template_id = self.env.ref('wt_mrp_cost.mail_template_bom_approval').id
        template = self.env['mail.template'].sudo().browse(template_id)
        company_id = self.company_id
        self.responsible_id = self.env.user
        bom_approver_users = self.env.ref('wt_mrp_cost.group_bom_recipe_manager')
        
        if company_id and bom_approver_users and bom_approver_users.users:
            
            # Filter users belonging to the same company
            allow_users = bom_approver_users.users.filtered(lambda u: company_id.id in u.company_ids.ids)
            email_list = [user.partner_id.email for user in allow_users if user.partner_id.email]
            email_values = {
                'email_from': self.responsible_id.email or self.env.user.email or 'default@example.com',
                'recipient_ids': [(6, 0, allow_users.mapped('partner_id').ids)],
            }
            template.send_mail(self.id, force_send=True, email_values=email_values)

        self.state = 'waiting_approval'

    def action_approve(self):
        if not self.env.user.has_group('wt_mrp_cost.group_bom_recipe_manager'):
            raise UserError(_("You can only approve requests without the correct role!"))
        
        template = self.env.ref('wt_mrp_cost.mail_template_bom_req_approved')
        if template:
            template.send_mail(self.id, force_send=True)
        self.state = 'approve'

    def action_reject(self):
        if not self.env.user.has_group('wt_mrp_cost.group_bom_recipe_manager'):
            raise UserError(_("You can not reject!"))
        return {
            'name': _('Reject BOM Request'),
            'type': 'ir.actions.act_window',
            'res_model': 'bom.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_bom_id': self.id},
        }

    def action_change_request(self):
        self.responsible_id = self.env.user
        template_id = self.env.ref('wt_mrp_cost.mail_template_bom_change_request').id
        template = self.env['mail.template'].sudo().browse(template_id)
        company_id = self.company_id
        bom_approver_users = self.env.ref('wt_mrp_cost.group_bom_recipe_manager')
        if company_id and bom_approver_users and bom_approver_users.users:
            allow_users = bom_approver_users.users.filtered(lambda u: company_id.id in u.company_ids.ids)
            email_list = [user.partner_id.email for user in allow_users if user.partner_id.email]
            email_values = {
                'email_from': self.responsible_id.email or self.env.user.email or 'default@example.com',
                'recipient_ids': [(6, 0, allow_users.mapped('partner_id').ids)],
            }
            template.send_mail(self.id, force_send=True, email_values=email_values)
            
        self.state = 'waiting_approval'

    @api.model
    def _bom_find_domain(self, products, picking_type=None, company_id=False, bom_type=False):
        domain = super()._bom_find_domain(products, picking_type=picking_type, company_id=company_id, bom_type=bom_type)
        domain = AND([domain, [('state', '=', 'approve')]])
        return domain



    def write(self, vals):
        for bom in self:
            old_data = {}
            if 'bom_line_ids' in vals:
                for line in bom.bom_line_ids:
                    old_data[line.id] = {
                        'product': line.product_id.display_name,
                        'product_id': line.product_id.id,
                        'qty': line.product_qty,
                        'cost': line.cost,
                    }

        result = super().write(vals)
        for bom in self:
            if 'bom_line_ids' in vals:
                message = ""
                for line in bom.bom_line_ids:
                    if line.id in old_data:
                        old = old_data[line.id]

                        if (
                            old['product_id'] != line.product_id.id or
                            old['qty'] != line.product_qty or
                            old['cost'] != line.cost
                        ):
                            message += (
                                f"Product: {old['product']} -> {line.product_id.display_name}\n"
                                f"Qty: {old['qty']} -> {line.product_qty}\n"
                                f"Cost: {old['cost']} -> {line.cost}\n\n"
                            )

                if message:
                    bom.message_post(body=message.strip())

            return result

    def get_constrains_domain(self):
        return [
            ('id','!=',self.id),
            ('company_id','=',self.company_id.id if self.company_id else False),
            ('product_id','=',self.product_id.id),
            ('type','=',self.type),
            ]

    def get_constrains_fields(self):
        return ['Product', 'BoM Type', 'Company']

    # @api.constrains('product_id', 'type','company_id')
    # def _constraint_bom_duplicate(self):
    #     fields  = self.get_constrains_fields()
    #     for rec in self:
    #         domain = rec.get_constrains_domain()
    #         records = self.search(domain)
    #         if records:
    #             raise ValidationError(_("Record already exist with sem data. \n %s", ", ".join(fields)))
