# -*- coding: utf-8 -*-
##########################################################################
#
#  Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#  See LICENSE file for full copyright and licensing details.
#  License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, fields, models


class WkSkeleton(models.TransientModel):
    _inherit = 'wk.skeleton'

    @api.model
    def turn_odoo_connection_off(self):
        """ To be inherited by bridge module for making
        connection Inactive on Odoo End"""
        res = super(WkSkeleton, self).turn_odoo_connection_off()
        activeConObj = self.env['magento.configure'].search(
            [('active', '=', True)])
        if activeConObj:
            if activeConObj[0].state == 'enable':
                activeConObj[0].state = 'disable'
        return res

    @api.model
    def turn_odoo_connection_on(self):
        """ To be inherited by bridge module for making connection
        Active on Odoo End"""
        res = super(WkSkeleton, self).turn_odoo_connection_on()
        activeConObj = self.env['magento.configure'].search(
            [('active', '=', True)])
        if activeConObj:
            activeConObj[0].state = 'enable'
        return res

    @api.model
    def set_extra_values(self):
        """ Add extra values"""
        res = super(WkSkeleton, self).set_extra_values()
        ctx = dict(self._context or {})
        pickingData = {}
        if 'picking_id' in ctx and 'carrier_tracking_ref' in ctx \
                and 'carrier_code' in ctx and 'mage_ship_number' in ctx:
            pickingData = {
                'carrier_tracking_ref': ctx.get(
                    'carrier_tracking_ref',  False),
                'carrier_code': ctx.get('carrier_code', 'custom'),
                'magento_shipment': ctx.get('mage_ship_number', False)
            }
        elif 'mage_ship_number' in ctx:
            pickingData = {
                'magento_shipment': ctx.get('mage_ship_number')
            }

        if pickingData:
            pickingObj = self.env['stock.picking'].browse(
                ctx.get('picking_id'))
            pickingObj.write(pickingData)
        return res

    @api.model
    def get_magento_configuration_data(self):

        IrConfigPrmtr = self.env['ir.config_parameter'].sudo()
        mobSalesTeam = IrConfigPrmtr.get_param(
            'odoo_magento_connect.mob_sales_team'
        )
        mobSalesPerson = IrConfigPrmtr.get_param(
            'odoo_magento_connect.mob_sales_person'
        )
        mobPaymentTerm = IrConfigPrmtr.get_param(
            'odoo_magento_connect.mob_payment_term'
        )
        return {
            'team_id': mobSalesTeam and int(mobSalesTeam),
            'user_id': mobSalesPerson and int(mobSalesPerson),
            'payment_term_id': mobPaymentTerm and int(mobPaymentTerm)
        }

    @api.model
    def create_sale_order_line(self, data):
        if 'tax_id' in data:
            taxes = data.get('tax_id')
            if not isinstance(taxes, list):
                taxes = [data.get('tax_id')]
            data['tax_id'] = [(6, 0, taxes)]
        else:
            data['tax_id'] = False
        return super(WkSkeleton, self).create_sale_order_line(data)

    @api.model
    def get_magento_virtual_product_id(self, data):
        odooProductId = False
        virtualName = data.get('name')[0]
        if virtualName == 'S':
            carrierObj = self.env['sale.order'].browse(
                data['order_id']).carrier_id
            odooProductId = carrierObj.product_id.id
            return odooProductId
        IrConfigPrmtr = self.env['ir.config_parameter'].sudo()
        defProductObj = {
            'D': "mob_discount_product",
            'V': "mob_coupon_product",
        }[virtualName]
        configProd = 'odoo_magento_connect.' + defProductObj
        odooProductId = IrConfigPrmtr.get_param(configProd)
        if not odooProductId:
            tempDict = {
                'sale_ok': False,
                'name': data.get('name'),
                'type': 'service',
                'list_price': 0.0,
            }
            defProductDesc = {
                'D': ("Service Type product used by Magento Odoo "
                      "Bridge for Discount Purposes"),
                'V': ("Service Type product used by Magento Odoo "
                      "Bridge for Gift Voucher Purposes"),
            }[virtualName]
            tempDict.update({
                'description': defProductDesc
            })
            odooProductId = self.env['product.product'].create(tempDict).id
            IrConfigPrmtr.set_param(configProd, odooProductId)
        else:
            odooProductId = odooProductId and int(odooProductId)
        return odooProductId

    @api.model
    def create_order_mapping(self, mapData):
        ctx = dict(self._context or {})
        mapData['instance_id'] = ctx.get('instance_id')
        return super(WkSkeleton, self).create_order_mapping(mapData)

    @api.model
    def create_order_invoice(self, orderId, ecommerceInvoiceId=False):
        ctx = dict(self._context or {})
        res = super(WkSkeleton, self).create_order_invoice(
            orderId, ecommerceInvoiceId)
        if 'invoice_date' in ctx and 'invoice_id' in res:
            accountObj = self.env['account.invoice'].browse(res['invoice_id'])
            accountObj.write(
                {'date_invoice': ctx.get('invoice_date'),
                 'date_due': ctx.get('invoice_date')})
        return res


class WkOrderMapping(models.Model):
    _inherit = "wk.order.mapping"

    instance_id = fields.Many2one(
        'magento.configure', string='Magento Instance')
