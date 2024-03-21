from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Nguyenlieu(models.Model):
    _name = "nguyen.lieu"
    _rec_name = 'tennguyenlieu'

    manguyenlieu = fields.Char(string="Mã nguyên liệu", required=True)
    tennguyenlieu = fields.Char(string="Tên nguyên liệu")
    nhomnguyenlieu = fields.Many2one('nhom.nguyen.lieu', 'Nhóm nguyên liệu')
    donvitinh = fields.Many2one('don.vi.tinh', 'Đơn vị tính')
    nhua = fields.Boolean('Nhựa')

    @api.constrains('manguyenlieu')
    def _check_manguyenlieu_unique(self):
        # check không cho 2 mã nguyên liệu được tạo cùng lúc
        for record in self:
            existing = self.search([('manguyenlieu', '=', record.manguyenlieu), ('id', '!=', record.id)])
            if existing:
                raise ValidationError(_("Mã nguyên liệu %s đã tồn tại trong hệ thống!" % record.manguyenlieu))


class Nhomnguyenlieu(models.Model):
    _name = "nhom.nguyen.lieu"
    _rec_name = 'tennhom'

    manhom = fields.Char('Mã nhóm nguyên liệu')
    tennhom = fields.Char('Tên nhóm nguyên liệu')
    nhomcha = fields.Many2one('nhom.nguyen.lieu', 'Nhóm nguyên liệu cha')
    # nguyenlieucha = fields.Boolean('Là nhóm nguyên liệu cha')
