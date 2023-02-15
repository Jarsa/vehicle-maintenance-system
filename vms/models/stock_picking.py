# Copyright 2016-2022, Jarsa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from odoo.tools.sql import column_exists, create_column


class StockPicking(models.Model):
    _inherit = "stock.picking"

    vms_order_id = fields.Many2one(
        related="group_id.vms_order_id",
        string="VMS Order",
        store=True,
        readonly=True,
    )

    def _auto_init(self):
        """
        Create related field here, too slow
        when computing it afterwards through _compute_related.

        Since group_id.vms_order_id is created in this module,
        no need for an UPDATE statement.
        """
        if not column_exists(self.env.cr, "stock_picking", "vms_order_id"):
            create_column(self.env.cr, "stock_picking", "vms_order_id", "int4")
        return super()._auto_init()
