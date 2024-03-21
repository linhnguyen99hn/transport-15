# -*- coding: utf-8 -*-

from odoo import models, fields, api

from datetime import datetime, timedelta

from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT


class Tinhtienkehoach(models.TransientModel):
    _name = 'tinh.tien.ke.hoach'
    _rec_name = 'date_start'

    date_start = fields.Date('Từ ngày')
    date_end = fields.Date('Đến ngày')
    lenhsx_ids = fields.Many2one('lenh.san.xuat', 'Lệnh sản xuất')
    donhang = fields.Many2one('don.hang', 'Đơn hàng')
    donhangchitiet_id = fields.Many2one('donhang.chitiet', 'Sản phẩm', domain="[('donhang_id', '=?', donhang)]")
    sanpham = fields.Many2one('dm.sanpham', 'Sản phẩm')
    masx = fields.Many2one('cong.thuc.phoi.tron', 'Mã sản xuất', compute='tinh_manoibo', store=True)
    kh_may_id = fields.Many2one('dm.may', 'Máy chạy')

    thoigian_tinhtien = fields.Float('Thời gian (giờ)')

    @api.depends('sanpham')
    def tinh_manoibo(self):
        for rec in self:
            if rec.sanpham:
                rec.masx = rec.sanpham.manoibosp

    def tinh_tien_kehoach(self):
        domain = []

        if self.date_start:
            domain = expression.AND([domain, [('ngay', '>=', self.date_start)]])
        if self.date_end:
            domain = expression.AND([domain, [('ngay', '<=', self.date_end)]])
        if self.kh_may_id:
            domain = expression.AND([domain, [('kh_may_id', '=', self.kh_may_id.id)]])
        if self.lenhsx_ids:
            domain = expression.AND([domain, [('lenhsx_ids', '=', self.lenhsx_ids.id)]])
        if self.donhang:
            domain = expression.AND([domain, [('donhang', '=', self.donhang.id)]])
        if self.sanpham:
            domain = expression.AND([domain, [('sanpham', '=', self.sanpham.id)]])
        if self.masx:
            domain = expression.AND([domain, [('masx', '=', self.masx.id)]])

        kehoachs = self.env['kehoach.sanxuat'].search(domain)
        for r in kehoachs:
            tg_batdau = r.thoigian_batdau
            tg_ketthuc = r.thoigian_ketthuc
            if tg_batdau:
                if tg_ketthuc:
                    r.write({'thoigian_ketthuc': tg_ketthuc + timedelta(hours=self.thoigian_tinhtien)})
                else:
                    if r.thoigian_dukien:
                        r.write({'thoigian_ketthuc': tg_batdau + timedelta(hours=self.thoigian_tinhtien) + timedelta(hours=r.thoigian_dukien)})
                r.write({'thoigian_batdau': tg_batdau + timedelta(hours=self.thoigian_tinhtien)})
        return self.thong_bao_thanh_cong()


    # -----Thông báo thực hiện thành công-------------------------------
    def thong_bao_thanh_cong(self):
        message_success = self.env.ref('mrp_fm.message_success_tinh_tien_ke_hoach_form_view')
        return {
            'name': 'Thông báo',
            'type': 'ir.actions.act_window',
            'res_model': 'tinh.tien.ke.hoach',
            'view_mode': 'form',
            'view_id': message_success.id,
            'target': 'new',
        }
    def reload_list_view(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
