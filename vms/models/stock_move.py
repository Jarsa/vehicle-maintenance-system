# Copyright 2016-2022, Jarsa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    vms_product_line_id = fields.Many2one(
        "vms.product.line", "VMS Product Line", index=True
    )

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        distinct_fields = super()._prepare_merge_moves_distinct_fields()
        distinct_fields.append("vms_product_line_id")
        return distinct_fields

    def _get_source_document(self):
        res = super()._get_source_document()
        return self.vms_product_line_id.order_id or res

    def _assign_picking_post_process(self, new=False):
        res = super()._assign_picking_post_process(new=new)
        if new:
            picking_id = self.mapped("picking_id")
            vms_order_ids = self.mapped("vms_product_line_id.order_id")
            for vms_order_id in vms_order_ids:
                picking_id.message_post_with_view(
                    "mail.message_origin_link",
                    values={"self": picking_id, "origin": vms_order_id},
                    subtype_id=self.env.ref("mail.mt_note").id,
                )
        return res
