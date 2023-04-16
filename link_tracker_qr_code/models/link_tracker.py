# -*- coding: utf-8 -*-

import base64
import io
import qrcode
import logging

from PIL import Image

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class LinkTracker(models.Model):
    _inherit = "link.tracker"

    qr_code = fields.Binary(string='QR Code', attachment=True, store=True)
    # qr_code_logo = fields.Image(string='QR Code Center Image', attachment=True, store=True)
    use_company_logo = fields.Boolean(string='Use Company Logo', default=False)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    @api.model
    def create(self, vals):
        _logger.info('LinkTracker creating.........')
        link_tracker = super(LinkTracker, self).create(vals)
        if link_tracker:
            qr_code_image = qrcode.make(link_tracker.short_url)

            if self.use_company_logo:
                if not self.company_id or not self.company_id.logo:
                    raise UserError(_('Please set a logo for the company.'))

                logo_image = Image.open(io.BytesIO(self.company_id.logo))
                
                # Resize the logo to fit in the center of the QR code
                logo_size = min(qr_code_image.size) // 3
                logo_image = logo_image.resize((logo_size, logo_size))

                # Calculate the position to paste the logo in the center of the QR code
                logo_position = ((qr_code_image.size[0] - logo_size) // 2, (qr_code_image.size[1] - logo_size) // 2)

                # Paste the logo onto the QR code image
                qr_code_image = qr_code_image.convert('RGB')

                pos = (250, 250)
                qrcode.paste(logo, pos)
            

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
