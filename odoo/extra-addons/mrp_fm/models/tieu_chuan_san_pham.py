from odoo import _, api, fields, models, SUPERUSER_ID, tools
from odoo.exceptions import ValidationError, UserError


class Tieuchuansanphamtaohat(models.Model):
    _name = "tieu.chuan.tao.hat"

    masx_ids = fields.Many2one('cong.thuc.phoi.tron', 'Công thức phối trộn')
    noidungkiemtra = fields.Char('Nội dung kiểm tra')
    tieuchuansanpham = fields.Char('Tiêu chuẩn sản phẩm')
    ghichu = fields.Char('Ghi chú')
