from odoo import _, api, fields, models, SUPERUSER_ID, tools
from odoo.exceptions import ValidationError, UserError


class Nhietdo(models.Model):
    _name = "nhiet.do"
    _rec_name = 'ma'

    ma = fields.Char('Mã')
    dh1 = fields.Float('DH01')
    dh2 = fields.Float('DH02')
    dh3 = fields.Float('DH03')
    dh4 = fields.Float('DH04')
    dh5 = fields.Float('DH05')
    dh6 = fields.Float('DH06')
    dh7 = fields.Float('DH07')
    dh8 = fields.Float('DH08')
    dh9 = fields.Float('DH09')
    dh10 = fields.Float('DH010')
    dh11 = fields.Float('DH011')
    dh12 = fields.Float('DH012')
    dh13 = fields.Float('DH013')
    dh14 = fields.Float('DH014')

