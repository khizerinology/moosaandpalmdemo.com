# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class BOMRejectWizard(models.TransientModel):
    _name = 'bom.reject.wizard'
    _description = 'Reject BOM Request'

    bom_id = fields.Many2one('mrp.bom', string="BOM", required=True, readonly=True)
    reject_reason = fields.Text(string="Rejection Reason", required=True)

    def action_confirm_reject(self):
        """ Set rejection reason, update state, and send rejection email to responsible user """
        if not self.env.user.has_group('wt_mrp_cost.group_bom_recipe_manager'):
            raise UserError(_("You can only approve requests without the correct role!"))
        if not self.reject_reason.strip():
            raise UserError("Please write a reason for rejection.")

        self.bom_id.write({
            'state': 'reject',
            'reject_reason': self.reject_reason,
        })
        template = self.env.ref('wt_mrp_cost.mail_template_bom_request_reject')
        if template:
            template.send_mail(self.bom_id.id, force_send=True)
