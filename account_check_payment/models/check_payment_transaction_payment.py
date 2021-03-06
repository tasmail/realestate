# -*- coding: utf-8 -*-
##############################################################################
#
#   Check Payment
#   Authors: Dominador B. Ramos Jr. <mongramosjr@gmail.com>
#   Company: Basement720 Technology Inc.
#
#   Copyright 2018 Dominador B. Ramos Jr.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
##############################################################################
import datetime

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class CheckPaymentTransactionPayment(models.Model):

    _name = 'check.payment.transaction.payment'
    _description = 'Check Payment'
    _inherits = {'check.payment.transaction': 'check_payment_transaction_id'}

    check_payment_transaction_id = fields.Many2one('check.payment.transaction', required=True, string='Payment Reference', ondelete='cascade')
    account_payment_id = fields.Many2one('account.payment', readonly=True, string='Payment Reference', ondelete='cascade', index=True, states={'draft': [('readonly', False)]})


    @api.multi
    def _compute_payment_type(self):
        for rec in self:
            if rec.account_payment_id:
                if rec.account_payment_id.payment_type == 'inbound':
                    rec.payment_type = rec.account_payment_id.payment_type
                elif rec.account_payment_id.payment_type == 'outbound':
                    rec.payment_type = rec.account_payment_id.payment_type
            else:
                rec.payment_type = 'inbound'

    @api.model
    def create(self, vals):
        
        if vals.get('account_payment_id', False):
            account_payment = self.env['account.payment'].browse(vals['account_payment_id'])
            vals['journal_id'] = account_payment.journal_id.id
            vals['partner_id'] = account_payment.partner_id.id
            vals['currency_id'] = account_payment.currency_id.id
            if account_payment.payment_type == 'inbound':
                vals['payment_type'] = 'inbound'
            elif account_payment.payment_type == 'outbound':
                vals['payment_type'] = 'outbound'
        
        res = super(CheckPaymentTransactionPayment, self).create(vals)
        
        return res

    @api.multi
    def action_receive(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("Only a check with status draft can be received."))

            rec.name = rec.check_name + ' ' + rec.check_number
            rec.write({'state': 'received'})

    @api.multi
    def action_issue(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("Only a check with status draft can be issued."))

            rec.name = rec.check_name + ' ' + rec.check_number
            rec.write({'state': 'issued'})
