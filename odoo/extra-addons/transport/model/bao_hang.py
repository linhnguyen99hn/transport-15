from odoo import api, fields, models, SUPERUSER_ID, tools
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta, time


class Baohang(models.Model):
    _name = "bao.hang"
    _rec_name = 'khachhang'

    khachhang = fields.Many2one('khach.hang', string="Khách hàng")
    makhachhang = fields.Many2one('khach.hang.con', string="Mã khách hàng")
    ngayphat = fields.Date('Ngày phát')
    khovanchuyen = fields.Many2one('kho.van.chuyen', string="Kho vận chuyển")
    loaihanghoa = fields.Char('Loại hàng hóa')
    mahanghoa = fields.Char('Mã hàng hóa')
    khophat = fields.Char('Kho phát')
    dongiakhovc = fields.Float('Đơn giá kho vận chuyển')
    thanhtienkhovc = fields.Float('Thành tiền kho vận chuyển', compute='tinh_thanh_tien_kho_vc', store=True)
    ngaynhan = fields.Date('Ngày nhận')
    ngaygiao = fields.Date('Ngày giao')
    malo = fields.Char('Mã lô')
    socan = fields.Float('Số cân') #chỉnh sửa kiểu dữ liệu trường số cân cho đúng yêu cầu, chỉnh xong xóa
    # tientrinh = fields.Many2many('tien.trinh', relation='tientrinh_baohang',string='Tiến trình',) # widget='many2many_tags'
    thanhtiendoitac = fields.Float('Thành tiền đối tác')
    ghichu = fields.Char('Ghi chú')

    @api.depends('dongiakhovc')
    def tinh_thanh_tien_kho_vc(self):
        return

