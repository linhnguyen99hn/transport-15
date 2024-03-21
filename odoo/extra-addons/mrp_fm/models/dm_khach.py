from odoo import _, api, fields, models, SUPERUSER_ID, tools
from odoo.exceptions import ValidationError, UserError


class DmKhach(models.Model):
    _name = "dm.khach"
    _rec_name = 'makhach'

    makhach = fields.Char('Mã khách')
    tenkhach = fields.Char('Tên khách')
    diachi = fields.Char('Địa chỉ')
    sodienthoai = fields.Char('Số điện thoại')
    email = fields.Char('Email')
    avatar = fields.Image('avatar', max_width=128, max_height=128)
    phanloaikhach = fields.Selection([('mua', 'Khách mua'), ('ban', 'Khách bán')], 'Phân loại')
    code_filler = fields.One2many('code.filler.khach', 'khachhang_ids', 'Code filler')

class DmKhach(models.Model):
    _name = "code.filler.khach"
    _rec_name = 'code_filler'

    code_filler = fields.Many2one('cong.thuc.phoi.tron', 'Code filler')
    khachhang_ids = fields.Many2one('dm.khach', 'Khách hàng')
