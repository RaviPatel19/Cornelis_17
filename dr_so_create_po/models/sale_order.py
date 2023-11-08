# -*- coding: utf-8 -*-
# Copyright (c) 2019-Present Droggol. (<https://www.droggol.com/>)

from odoo import _, api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    dr_purchase_order_count = fields.Integer(compute='_compute_dr_purchase_order_count', copy=False, default=0)
    dr_purchase_order_ids = fields.One2many('purchase.order', 'dr_sale_order_id')

    def _compute_dr_purchase_order_count(self):
        Purchase = self.env['purchase.order'].sudo()
        for order in self:
            purchase_ids = order.dr_purchase_order_ids.ids + Purchase.search([('origin', '=', order.name)]).ids
            order.dr_purchase_order_count = len(list(set(purchase_ids)))

    def action_view_purchase_orders(self):
        purchase_ids = self.dr_purchase_order_ids.ids + self.env['purchase.order'].sudo().search([('origin', '=', self.name)]).ids
        action = self.env.ref('purchase.purchase_rfq').read()[0]
        action['domain'] = "[('id','in',%s)]" % (list(set(purchase_ids)))
        return action


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    dr_reserved_qty = fields.Float(compute='_compute_dr_reserved_qty', digits='Product Unit of Measure')

    def _compute_dr_reserved_qty(self):
        for line in self:
            line.dr_reserved_qty = sum(line.order_id.picking_ids.move_ids.filtered(lambda x: x.product_id.id == line.product_id.id).mapped('availability'))
