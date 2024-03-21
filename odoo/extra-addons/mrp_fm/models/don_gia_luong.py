from odoo import _, api, fields, models, SUPERUSER_ID, tools
from odoo.exceptions import ValidationError, UserError


class DmDongialuong(models.Model):
    _name = "don.gia.luong"
    _rec_name = 'ten'

    ten = fields.Char('Loại nhân công')
    # dongia = fields.Float('Đơn giá')
