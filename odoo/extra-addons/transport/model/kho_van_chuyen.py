from odoo import api, fields, models, SUPERUSER_ID, tools
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta, time


class Khovanchuyen(models.Model):
    _name = "kho.van.chuyen"
    _rec_name = 'tenkho'

    tenkho = fields.Char('Kho vận chuyển')
    sodienthoai = fields.Char('Số điện thoại')
    ghichu = fields.Char('Ghi chú')
