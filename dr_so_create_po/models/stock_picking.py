# -*- coding: utf-8 -*-
# Copyright (c) 2019-Present Droggol. (<https://www.droggol.com/>)

from odoo import _, api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    dr_po_from_so_id = fields.Many2one(string='PO From SO', related='purchase_id.dr_sale_order_id', store=True)

    def action_view_sale_order(self):
        action = self.env.ref('sale.action_quotations_with_onboarding').read()[0]
        action['res_id'] = self.dr_po_from_so_id.id
        action['views'] = [[False, 'form']]
        return action

    def action_view_td_sale_order(self):
        action = self.env.ref('sale.action_quotations_with_onboarding').read()[0]
        action['res_id'] = self.sale_id.id
        action['views'] = [[False, 'form']]
        return action
