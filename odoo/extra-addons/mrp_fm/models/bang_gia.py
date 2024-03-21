from odoo import fields, models


class DmBanggia(models.Model):
    _name = "bang.gia"
    _rec_name = 'ten'
    _order = "tungay desc, denngay desc"

    ten = fields.Char('Tên bảng giá')
    tungay = fields.Date(string="Từ ngày")
    denngay = fields.Date('Đến ngày')
    gianguyenlieu = fields.One2many('gia.nguyen.lieu', 'bang_gia_ids', 'Giá nguyên liệu chi tiết')




class Gianguyenlieu(models.Model):
    _name = "gia.nguyen.lieu"

    bang_gia_ids = fields.Many2one('bang.gia', 'Bảng giá')
    nguyenlieu = fields.Many2one('nguyen.lieu', 'Nguyên liệu')
    manguyelieu = fields.Char(string="Tên nguyên liệu", related="nguyenlieu.manguyenlieu")
    donvitinh = fields.Char("Đơn vị tính", related="nguyenlieu.donvitinh.donvitinh")
    dongia = fields.Float('Đơn giá')
