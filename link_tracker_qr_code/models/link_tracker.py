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
    
    @api.model_create_multi
    def create(self, vals_list):
        res = super(LinkTracker, self).create(vals_list)
        for link_tracker in res:
            if link_tracker:
                qr_code_image = qrcode.make(link_tracker.short_url)

                if link_tracker.use_company_logo:
                    if not link_tracker.company_id or not link_tracker.company_id.logo:
                        raise UserError(_('Please set a logo for the company.'))

                    _logger.info('Binary data: %s', link_tracker.company_id.id)

                    # logo_image = Image.open(io.BytesIO(link_tracker.company_id.logo))
                    # logo_data = io.BytesIO(link_tracker.company_id.logo)
                    try:
                        # Image.open(logo_data).verify()  # Verify the image format
                        # logo_data.seek(0)  # Reset the BytesIO position
                        # logo_image = Image.open(logo_data)
                        logo_binary_data = base64.b64decode(link_tracker.company_id.logo)
                        logo_image = Image.open(io.BytesIO(logo_binary_data))
                        
                        # Resize the logo to fit in the center of the QR code
                        logo_size = min(qr_code_image.size) // 4
                        logo_image = logo_image.resize((logo_size, logo_size))

                        # Calculate the position to paste the logo in the center of the QR code
                        logo_position = ((qr_code_image.size[0] - logo_size) // 2, (qr_code_image.size[1] - logo_size) // 2)

                        # Paste the logo onto the QR code image
                        qr_code_image = qr_code_image.convert('RGB')

                        pos = ((qr_code_image.size[0] - logo_image.size[0]) // 2,
                                (qr_code_image.size[1] - logo_image.size[1]) // 2)
                        qr_code_image.paste(logo_image, pos)
                    except Exception as e:
                        raise UserError(_('The company logo has an invalid format: %s') % str(e))

                

                buffer = io.BytesIO()
                qr_code_image.save(buffer, format='PNG')
                buffer.seek(0)
                link_tracker.qr_code = base64.b64encode(buffer.read())
                _logger.info('LinkTracker created...........')
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
