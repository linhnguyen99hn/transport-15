from odoo import _, api, fields, models, SUPERUSER_ID, tools
from odoo.exceptions import ValidationError, UserError


class DmSanpham(models.Model):
    _name = "dm.sanpham"
    _rec_name = 'mathuongmaisp'

    mathuongmaisp = fields.Char('Mã thương mại')
    makhach = fields.Many2one('dm.khach', 'Mã khách')
    manoibosp = fields.Many2one('cong.thuc.phoi.tron', 'Code filler', store='True')
    dinhmuc = fields.One2many('cong.thuc', 'sanpham_ids', 'Định mức phần trăm', inverse='set_dinh_muc', compute='dinh_muc_phan_tram', readonly=True)
    tensanpham = fields.Char('Tên sản phẩm')

    trongluong = fields.Float('Trọng lượng bao (kg)', default=25)
    trongluongpallet = fields.Float('Trọng lượng pallet (kg)')

    mathuongmaisp_id = fields.One2many('congsuat.may', 'sanpham_ids', 'Sản phẩm')

    quycachsanpham_ids = fields.One2many('quycach.sanpham', 'sanpham_id', 'Quy cách sản phẩm')

    @api.depends('manoibosp')
    def dinh_muc_phan_tram(self):
        # cách1
        # if self.manoibosp:
        #     self.dinhmuc = self.manoibosp.dinhmuc

        # cách2
        domain = [('sanpham_ids', '=', self.manoibosp.id)]
        dinhmuc_records = self.env['cong.thuc'].search(domain)
        self.dinhmuc = dinhmuc_records

    def set_dinh_muc(self):
        self.manoibosp.dinhmuc = self.dinhmuc

class QuycachSanpham(models.Model):
    _name = 'quycach.sanpham'
    _rec_name = ''

    nhomquycach_id = fields.Many2one('dm.nhomquycach', 'Nhóm quy cách')
    quycach_id = fields.Many2one('dm.quycach', 'Quy cách')
    ten_nhomquycach = fields.Char('Quy cách', compute='_ten_nhomquycach', store=True)
    ten_quycach = fields.Char('Chi tiết', compute='_ten_quycach', store=True)

    mota_nhomquycach = fields.Text(related='nhomquycach_id.mota', store=True)
    mota_quycach = fields.Text(related='quycach_id.mota', store=True)

    sanpham_id = fields.Many2one('dm.sanpham', 'Sản phẩm')

    @api.depends('nhomquycach_id')
    def _ten_nhomquycach(self):
        for rec in self:
            rec.ten_nhomquycach = rec.nhomquycach_id.tennhom

    @api.depends('quycach_id')
    def _ten_quycach(self):
        for rec in self:
            rec.ten_quycach = rec.quycach_id.tenquycach
