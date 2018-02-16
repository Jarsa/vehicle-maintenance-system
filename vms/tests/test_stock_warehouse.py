# -*- coding: utf-8 -*-
# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestFleetVehicle(TransactionCase):

    def setUp(self):
        super(TestFleetVehicle, self).setUp()
        self.warehouse = self.env.ref('stock.warehouse0')

    def test_get_routes_dict(self):
        self.warehouse.write({
            'delivery_steps': 'pick_ship',
        })
        self.assertTrue(self.warehouse.wh_vms_out_picking_type_id)
