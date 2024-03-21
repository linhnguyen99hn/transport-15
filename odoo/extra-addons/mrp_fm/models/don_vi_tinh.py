from odoo import _, api, fields, models, SUPERUSER_ID, tools
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta


class Donvitinh(models.Model):
    _name = "don.vi.tinh"
    _rec_name = 'donvitinh'

    madonvitinh = fields.Char('Mã đơn vị tính')
    donvitinh = fields.Char('Đơn vị tính')
