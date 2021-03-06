# Copyright (C) 2009 - TODAY Renato Lima - Akretion
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models

from ..constants.fiscal import (NFE_IND_IE_DEST, NFE_IND_IE_DEST_9,
                                NFE_IND_IE_DEST_DEFAULT, TAX_FRAMEWORK,
                                TAX_FRAMEWORK_NORMAL)


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def _default_fiscal_profile_id(self, is_company=False):
        """Define o valor padão para o campo tipo fiscal, por padrão pega
        o tipo fiscal para não contribuinte já que quando é criado um novo
        parceiro o valor do campo is_company é false"""
        ft_ids = self.env["l10n_br_fiscal.partner.profile"].search(
            [("default", "=", "True"), ("is_company", "=", is_company)], limit=1
        )
        return ft_ids

    tax_framework = fields.Selection(
        selection=TAX_FRAMEWORK, default=TAX_FRAMEWORK_NORMAL, string="Tax Framework"
    )

    cnae_main_id = fields.Many2one(
        comodel_name="l10n_br_fiscal.cnae",
        domain="[('internal_type', '=', 'normal')]",
        string="Main CNAE",
    )

    ind_ie_dest = fields.Selection(
        selection=NFE_IND_IE_DEST,
        string=u"Contribuinte do ICMS",
        required=True,
        default=NFE_IND_IE_DEST_DEFAULT,
    )

    fiscal_profile_id = fields.Many2one(
        comodel_name="l10n_br_fiscal.partner.profile",
        string=u"Fiscal Partner Profile",
        inverse="_inverse_fiscal_profile",
        domain="[('is_company', '=', is_company)]",
        default=_default_fiscal_profile_id,
    )

    def _inverse_fiscal_profile(self):
        for p in self:
            p._onchange_fiscal_profile_id()

    @api.onchange("is_company")
    def _onchange_is_company(self):
        self.fiscal_profile_id = self._default_fiscal_profile_id(self.is_company)

    @api.onchange("fiscal_profile_id")
    def _onchange_fiscal_profile_id(self):
        for p in self:
            if p.fiscal_profile_id:
                p.tax_framework = p.fiscal_profile_id.tax_framework
                p.ind_ie_dest = p.fiscal_profile_id.ind_ie_dest

    @api.onchange("ind_ie_dest")
    def _onchange_ind_ie_dest(self):
        if self.ind_ie_dest == NFE_IND_IE_DEST_9:
            self.inscr_est = False
            self.state_tax_number_ids = False
