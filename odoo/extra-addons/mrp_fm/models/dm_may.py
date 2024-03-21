from odoo import _, api, fields, models, SUPERUSER_ID, tools
from odoo.exceptions import ValidationError, UserError


class DmMaysanxuat(models.Model):
    _name = "dm.may"
    _rec_name = 'mamay'

    mamay = fields.Char('Mã máy')
    tenmay = fields.Char('Tên máy')
    tinhtrang = fields.Selection([('hoatdong', 'Hoạt động'), ('nghi', 'Nghỉ')], 'Tình trạng', default='hoatdong')
    mota = fields.Char('Mô tả')

    mamay_id = fields.One2many('congsuat.may', 'may_ids', 'Máy')


class CongsuatMay(models.Model):
    _name = 'congsuat.may'
    _rec_name = 'congsuat'

    congsuat = fields.Float('Công suất (Kg/h)')
    mota = fields.Char('Ghi chú')

    sanpham_ids = fields.Many2many('dm.sanpham', column1='mathuongmaisp_id', column2='id', relation='cong_suat_may_voi_san_pham', string="Sản phẩm", widget='many2many_tags')
    may_ids = fields.Many2many('dm.may', column1='mamay_id', column2='id', relation='cong_suat_may_voi_may', string="Máy", widget='many2many_tags')


