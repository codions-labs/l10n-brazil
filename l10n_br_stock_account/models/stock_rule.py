# Copyright (C) 2020  Magno Costa - Akretion
# Copyright (C) 2016  Renato Lima - Akretion
# Copyright (C) 2016  Luis Felipe Miléo - KMEE
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models


class StockRule(models.Model):
    _inherit = 'stock.rule'

    @api.model
    def _default_fiscal_operation(self):
        return False

    @api.model
    def _fiscal_operation_domain(self):
        domain = [('state', '=', 'approved')]
        return domain

    fiscal_operation_id = fields.Many2one(
        comodel_name='l10n_br_fiscal.operation',
        string='Fiscal Operation',
        domain=lambda self: self._fiscal_operation_domain(),
        default=_default_fiscal_operation,
    )

    invoice_state = fields.Selection(
        selection=[
            ("2binvoiced", _("To Be Invoiced")),
            ("none", _("Not Applicable"))],
        string='Invoice Status',
        default='none',
        copy=False,
        help="Invoiced: an invoice already exists\n"
             "To Be Invoiced: need to be invoiced\n"
             "Not Applicable: no invoice to create",
    )

    def _get_custom_move_fields(self):
        """ The purpose of this method is to be override in order to
        easily add fields from procurement 'values' argument to move data.
        """
        custom_move_fields = super()._get_custom_move_fields()
        custom_move_fields += [
            'invoice_state',
            'fiscal_operation_id',
            'fiscal_operation_line_id',
        ]
        return custom_move_fields

    @api.model
    def run(self, product_id, product_qty, product_uom,
            location_id, name, origin, values):
        result = super().run(
            product_id, product_qty, product_uom,
            location_id, name, origin, values)
        return result