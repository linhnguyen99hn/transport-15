from odoo import _, api, fields, models, SUPERUSER_ID, tools
from odoo.exceptions import ValidationError, UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    scope = fields.Selection([('internal', 'Internal'), ('external', 'External')], 'Scope', default='external')
    code_filler = fields.Many2one('product.template', 'Code Filler', domain="[('scope', '=', 'internal')]")

    caco3 = fields.Float('Percentage CaCo3')
    tio2 = fields.Float('Percentage TiO2')
    mi = fields.Float('MI')
    other_standard = fields.Float('Other Standard')
