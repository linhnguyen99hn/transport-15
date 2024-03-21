from odoo import api, fields, models, SUPERUSER_ID, tools
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta, time


class Tientrinh(models.Model):
    _name = "tien.trinh"
    _rec_name = 'doitac'

    doitac = fields.Many2one('doi.tac')
    malo = fields.Char('Mã lô')
    ngaybatdau = fields.Date('Ngày bắt đầu')
    ngayketthuc = fields.Date('Ngày kết thúc')
    ghichu = fields.Char('Ghi chú')