# -*- coding: utf-8 -*-

import base64
import io
import qrcode
import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class LinkTracker(models.Model):
    _inherit = "link.tracker"

    qr_code = fields.Binary(string='QR Code', attachment=True, store=True)

    @api.model
    def create(self, vals):
        _logger.info('LinkTracker creating...........')
        link_tracker = super(LinkTracker, self).create(vals)
        if link_tracker:
            qr_code_image = qrcode.make(link_tracker.short_url)
            buffer = io.BytesIO()
            qr_code_image.save(buffer, format='PNG')
            buffer.seek(0)
            link_tracker.qr_code = base64.b64encode(buffer.read())
            _logger.info('LinkTracker created...........')
        return link_tracker
    
    @api.model_create_multi
    def create(self, vals_list):
        res = super(LinkTracker, self).create(vals_list)
        for link_tracker in res:
            if link_tracker:
                qr_code_image = qrcode.make(link_tracker.short_url)
                buffer = io.BytesIO()
                qr_code_image.save(buffer, format='PNG')
                buffer.seek(0)
                link_tracker.qr_code = base64.b64encode(buffer.read())
        return res
    
    def download_qr_code(self, *args, **kwargs):
        self.ensure_one()
        if not self.qr_code:
            raise UserError(_("No QR code available for this link."))

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/link.tracker/{}/qr_code/qr_code.png?download=true'.format(self.id),
            'target': 'new'
        }
