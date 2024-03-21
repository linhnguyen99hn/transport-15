from odoo import _, api, fields, models, SUPERUSER_ID, tools
from odoo.exceptions import ValidationError, UserError


class Tieuchuanthietbiphoitron(models.Model):
    _name = "tieu.chuan.thiet.bi"

    masx_ids = fields.Many2one('cong.thuc.phoi.tron', 'Công thức phối trộn')
    noidung = fields.Char('Nội dung kiểm tra')
    tieuchuanthietbi= fields.Char('Tiêu chuẩn thiết bị')
    ghichu = fields.Char('Ghi chú')
