# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, exceptions, models


class VmsOrderLinePo(models.TransientModel):
    _name = 'vms.order.line.po.wizard'

    @api.model
    def make_po(self):
    	import ipdb; ipdb.set_trace()


