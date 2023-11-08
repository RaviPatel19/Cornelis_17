# -*- coding: utf-8 -*-
# Copyright (c) 2019-Present Droggol. (<https://www.droggol.com/>)

from odoo import _, api, fields, models


class SupplierInfo(models.Model):
    _inherit = 'product.supplierinfo'

    price = fields.Float(digits='Product Vendor Price')


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    dr_sale_order_id = fields.Many2one('sale.order', 'Sale Order')
    dr_is_extra_po = fields.Boolean('Is Extra PO?')

    def action_view_sale_order(self):
        action = self.env.ref('sale.action_quotations_with_onboarding').read()[0]
        action['res_id'] = self.dr_sale_order_id.id
        action['views'] = [[False, 'form']]
        return action

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        ProcurementGroup = self.env['procurement.group']
        procurements = []

        for order in self:
            if order.dr_is_extra_po and order.dr_sale_order_id:

                group_id = order.dr_sale_order_id.procurement_group_id
                if not group_id:
                    group_id = ProcurementGroup.create(order.dr_sale_order_id._get_procurement_group_vals())
                    order.dr_sale_order_id.procurement_group_id = group_id

                for line in order.order_line:
                    procurements.append(ProcurementGroup.Procurement(
                        line.product_id,
                        line.product_qty,
                        line.product_uom,
                        order.dr_sale_order_id.partner_shipping_id.property_stock_customer,
                        line.name, order.dr_sale_order_id.name, order.company_id, order.dr_sale_order_id._get_procurement_values(line.product_id, 0, group_id)))
        ProcurementGroup.run(procurements)
        return res


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _prepare_stock_moves(self, picking):
        res = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
        if len(res):
            res[0]['description_picking'] = self.name
        return res

    @api.onchange('product_qty', 'product_uom', 'company_id')
    def _compute_price_unit_and_date_planned_and_name(self):
        super(PurchaseOrderLine, self)._compute_price_unit_and_date_planned_and_name()
        if not self.price_unit:
            self.price_unit = self.product_id.standard_price
