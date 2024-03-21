from odoo import api, fields, models, SUPERUSER_ID, tools
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta, time


class Khachhang(models.Model):
    _name = "doi.tac"
    _rec_name = 'doitac'

    doitac = fields.Char('Đối tác')
    sodienthoai = fields.Char('Số điện thoại')
    diemnguon = fields.Many2one("res.country.state", string='Điểm ', ondelete='restrict',
                                domain="[('country_id', '=', 241)]")
    diemdich = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                               domain="[('country_id', '=', 241)]")
    dongia = fields.Float('Đơn giá')
    ghichu = fields.Char('Ghi chú')

