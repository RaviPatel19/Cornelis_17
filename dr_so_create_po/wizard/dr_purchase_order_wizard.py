# -*- coding: utf-8 -*-
# Copyright (c) 2019-Present Droggol. (<https://www.droggol.com/>)

from odoo import api, fields, models, _, Command


class PurchaseOrderWizard(models.TransientModel):
    _name = 'dr.purchase.order.wizard'
    _description = 'Purchase Order Wizard'

    @api.model
    def default_get(self, fields):
        res = super(PurchaseOrderWizard, self).default_get(fields)
        active_ids = self._context.get('active_ids')
        mto_route_id = self.env.ref('stock.route_warehouse0_mto').id
        if active_ids and len(active_ids) == 1:
            sale_order_id = self.env['sale.order'].browse(active_ids)
            res['sale_order_id'] = sale_order_id.id
            res['purchase_order_line_ids'] = [(0, 0, {
                'product_id': line.product_id.id,
                'name': line.name,
                'product_uom_qty': line.product_uom_qty,
                'product_uom': line.product_uom.id,
                'reserved_qty': line.dr_reserved_qty,
                'order_qty': line.product_uom_qty - line.dr_reserved_qty,
                'supplier_id': line.product_id.seller_ids and line.product_id.seller_ids[0].partner_id.id or False,
            }) for line in sale_order_id.order_line.filtered(lambda x: x.route_id.id != mto_route_id and not x.display_type)]
            return res
        return res

    sale_order_id = fields.Many2one('sale.order')
    purchase_order_line_ids = fields.One2many('dr.purchase.order.wizard.line', 'wizard_id')

    def action_reserve_max(self):
        # Run Check Availability
        for picking in self.sale_order_id.picking_ids:
            picking.filtered(lambda p: p.state == 'draft').action_confirm()
            moves = picking.mapped('move_ids').filtered(lambda move: move.state not in ('draft', 'cancel', 'done'))
            if moves:
                package_level_done = picking.mapped('package_level_ids').filtered(lambda pl: pl.is_done and pl.state == 'confirmed')
                package_level_done.write({'is_done': False})
                moves._action_assign()
                package_level_done.write({'is_done': True})

        # Compute Reserved Qty
        for line in self.purchase_order_line_ids:
            reserved_qty = sum(self.sale_order_id.picking_ids.move_ids.filtered(lambda x: x.product_id.id == line.product_id.id).mapped('availability'))
            line.reserved_qty = reserved_qty
            line.order_qty = line.product_uom_qty - reserved_qty

        action = self.env.ref('dr_so_create_po.dr_purchase_order_wizard_action').read()[0]
        action['res_id'] = self.id
        return action

    def action_create_purchase_order(self):
        valid_lines = self.purchase_order_line_ids.filtered(lambda x: x.is_order_line and x.supplier_id)
        if valid_lines:
            for supplier in valid_lines.mapped('supplier_id'):
                lines = []
                for line in valid_lines.filtered(lambda x: x.supplier_id.id == supplier.id):
                    sellers = line.product_id.seller_ids.filtered(lambda x: x.partner_id.id == supplier.id)
                    price = line.product_id.standard_price
                    if sellers:
                        price = sellers[0].price
                    lines.append(Command.create({
                        'product_id': line.product_id.id,
                        'name': line.name,
                        'product_qty': line.order_qty,
                        'price_unit': price,
                        'product_uom': line.product_uom.id,
                        'date_planned': fields.Datetime.today(),
                    }))

                purchase_order_id = self.env['purchase.order'].create({
                    'partner_id': supplier.id,
                    'dr_sale_order_id': self.sale_order_id.id,
                    'order_line': lines,
                })

                for order_line in purchase_order_id.order_line:
                    order_line._compute_tax_id()

    def action_create_extra_purchase_order(self):
        return {
            'name': _('Create Purchase Order'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'purchase.order',
            'target': 'new',
            'context': {
                'default_dr_sale_order_id': self.sale_order_id.id,
                'default_dr_is_extra_po': True
            }
        }


class PurchaseOrderWizardLine(models.TransientModel):
    _name = 'dr.purchase.order.wizard.line'
    _description = 'Purchase Order Wizard Line'

    wizard_id = fields.Many2one('dr.purchase.order.wizard', required=True)

    is_order_line = fields.Boolean()
    product_id = fields.Many2one('product.product', string='Product')
    name = fields.Char()
    product_uom_qty = fields.Float(string='Quantity Asked', digits='Product Unit of Measure')
    product_uom = fields.Many2one('uom.uom')
    reserved_qty = fields.Float(string='Reserved', digits='Product Unit of Measure')
    order_qty = fields.Float(string='To Order', digits='Product Unit of Measure')
    supplier_id = fields.Many2one('res.partner', string='Supplier')
    order_id = fields.Many2one('purchase.order')
