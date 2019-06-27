# -*- coding: utf-8 -*-
# Copyright 2009-2018 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class AccountAssetCompute(models.TransientModel):
    _name = 'account.asset.compute'
    _description = "Compute Assets"

    date_end = fields.Date(
        string='Date', required=True,
        default=fields.Date.today,
        help="All depreciation lines prior to this date will be automatically"
             " posted")
    note = fields.Text()

    @api.multi
    def asset_compute(self):
        assets = self.env['account.asset'].search(
            [('state', '=', 'open'), ('type', '=', 'normal')])
        created_move_ids, error_log = assets._compute_entries(
            self.date_end, check_triggers=True)

        if error_log:
            result_view = self.env.ref(
                'account_asset_management.'
                'account_asset_compute_view_form_result')
            self.note = _("Compute Assets errors") + ':\n' + error_log
            return {
                'name': _('Compute Assets result'),
                'res_id': self.id,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.asset.compute',
                'view_id': result_view.id,
                'target': 'new',
                'type': 'ir.actions.act_window',
                'context': {'asset_move_ids': created_move_ids},
            }

        return {
            'name': _('Created Asset Moves'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'domain': [('id', 'in', created_move_ids)],
            'type': 'ir.actions.act_window',
        }

    @api.multi
    def view_asset_moves(self):
        self.ensure_one()
        domain = [('id', 'in', self._context.get('asset_move_ids', []))]
        return {
            'name': _('Created Asset Moves'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'domain': domain,
            'type': 'ir.actions.act_window',
        }