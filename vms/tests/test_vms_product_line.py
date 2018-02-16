# -*- coding: utf-8 -*-
# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestVmsProductLine(TransactionCase):

    def setUp(self):
        super(TestVmsProductLine, self).setUp()
        self.product = self.env.ref('vms.product_product_vms_02')
        self.vms_prod_line = self.env.ref('vms.vms_product_line_01')

    def test_onchange_product_id(self):
        self.vms_prod_line.product_id = self.product.id
        self.vms_prod_line._onchange_product_id()
        self.assertEqual(
            self.vms_prod_line.product_uom_id, self.product.uom_id)
