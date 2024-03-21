# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class Baocaochiphi(models.TransientModel):
    _name = 'bao.cao.chi.phi'

    @api.depends('create_date')
    def name_get(self):
        result = []
        for record in self:
            name = record.create_date.strftime('%d-%m-%Y')
            result.append((record.id, name))
        return result

    lenhsx = fields.Many2one('lenh.san.xuat', 'Lệnh sản xuất số', required=True)
    manguyenlieu = fields.Char('Mã nguyên liệu')
    tennguyenlieu = fields.Char('Tên nguyên liệu')
    donvitinh = fields.Char('ĐVT')
    khoiluong = fields.Float('Khối lượng')
    dongia = fields.Float('Đơn giá')
    khoiluongdukien = fields.Float('Khối lượng dự kiến')

    def get_report(self):
        if not self.lenhsx.kehoach:
            raise UserError('Không tìm thấy kế hoạch liên quan đến lệnh sản xuất này. Vui lòng kiểm tra lại.')
        data = {
            'model': self._name,
            'ids': self.ids,
            'form': {
                'malenhsx': self.lenhsx.id, 'lenhsx': self.lenhsx.lenhsx, 'tongmesx': self.lenhsx.tongmesx,
                'tongnguyenlieucap': self.lenhsx.tongnguyenlieucap,
            },
        }

        action = self.env.ref('mrp_fm.bao_cao_chi_phi').report_action(self, data=data)
        return action


class Baocaochiphi(models.AbstractModel):
    _name = 'report.mrp_fm.bao_cao_chi_phi_document'

    @api.model
    def _get_report_values(self, docids, data=None):
        lenhsx = data['form']['lenhsx']
        malenhsx = data['form']['malenhsx']
        tongnguyenlieucap = data['form']['tongnguyenlieucap']
        tongmesx = data['form']['tongmesx']

        masx = self.env['kehoach.sanxuat'].search([('lenhsx_ids', '=', malenhsx)], limit=1).masx
        donhang = self.env['kehoach.sanxuat'].search([('lenhsx_ids', '=', malenhsx)], limit=1).donhang
        banggia = self.env['don.hang'].search([('id', '=', donhang.id)], limit=1).banggia
        idbangiga = banggia.id
        manoibo = self.env['cong.thuc.phoi.tron'].search([('id', '=', masx.id)]).tencongthuc

        param = {}
        param['lenhsx'] = malenhsx
        param['banggia'] = idbangiga

        query1 = """
            SELECT ct.manguyenlieu, nl.tennguyenlieu, dvt.donvitinh, ct.khoiluong, gnl.dongia
                , sum(khsx.khoiluong_dukien)
				, -2147483648 + ct.id As thutusapxep
            From lenh_san_xuat lsx
                LEFT JOIN kehoach_sanxuat khsx ON khsx.lenhsx_ids = lsx.id
                LEFT JOIN cong_thuc ct ON ct.sanpham_ids=khsx.masx
                LEFT JOIN bang_gia_hieu_luc(lsx.ngaycapthucte) gnl ON ct.nguyenlieu = gnl.nguyenlieu
                left join nguyen_lieu nl on ct.nguyenlieu = nl.id
                left join don_vi_tinh dvt on dvt.id=nl.donvitinh
            Where lsx.id = %(lenhsx)s
            Group by ct.manguyenlieu, nl.tennguyenlieu, dvt.donvitinh, ct.khoiluong, gnl.dongia, ct.id
            UNION ALL
            Select nl.manguyenlieu, nl.tennguyenlieu, dvt.donvitinh, vt.soluongkehoach, gnl.dongia
                , 0
				, vt.id As thutusapxep
            From lenh_san_xuat lsx
                Left Join lenh_cap_vat_tu vt On vt.lenhsx_id=lsx.id
                LEFT JOIN bang_gia_hieu_luc(lsx.ngaycapthucte) gnl ON vt.mavattu = gnl.nguyenlieu 
                left join nguyen_lieu nl on vt.mavattu = nl.id
                left join don_vi_tinh dvt on dvt.id=nl.donvitinh
            Where lsx.id = %(lenhsx)s
            Order by thutusapxep
                """
        self.env.cr.execute(query1, param)
        data_dinhmuc = self.env.cr.fetchall()
        _ids = []
        for line in data_dinhmuc:
            data_row = ({
                'manguyenlieu': str(line[0]),
                'tennguyenlieu': str(line[1]),
                'donvitinh': str(line[2]),
                'khoiluong': line[3],
                'dongia': line[4],
                'khoiluongdukien': line[5],
                'lenhsx': malenhsx,
            })
            _ids.append(self.env['bao.cao.chi.phi'].create(data_row).id)

        docs = self.env['bao.cao.chi.phi'].browse(_ids)

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'manoibo': manoibo,
            'tongnguyenlieucap': tongnguyenlieucap,
            'tongmesx': tongmesx,
            'docs': docs,
            'lenhsx': lenhsx,
        }
