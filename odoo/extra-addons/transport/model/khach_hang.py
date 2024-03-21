from odoo import api, fields, models, SUPERUSER_ID, tools
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta, time


class Khachhang(models.Model):
    _name = "khach.hang"
    _rec_name = 'hoten'

    hoten = fields.Char('Họ và tên')
    makhachhang_ids = fields.One2many('khach.hang.con', 'khachhang_id', 'Khách hàng con')
    sodienthoai = fields.Char('Số điện thoại')
    diachi = fields.Char('Địa chỉ')
    ghichu = fields.Char('Ghi chú')

class Khachhangtructhuoc(models.Model):
    _name = "khach.hang.con"

    khachhang_id = fields.Many2one('khach.hang', 'Khách hàng')
    makhachhang = fields.Char('Mã khách hàng')
    dongia = fields.Float('Đơn giá')