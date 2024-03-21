# -*- coding: utf-8 -*-

from odoo import models, fields, api
from operator import itemgetter
from datetime import datetime, timedelta

from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT


class BaocaonhucaunguyenlieuWizard(models.TransientModel):
    _name = 'bao.cao.nhu.cau.nguyen.lieu.wizard'

    # _rec_name = 'date_start'
    @api.depends('create_date')
    def name_get(self):
        result = []
        for record in self:
            name = record.create_date.strftime('%d-%m-%Y')
            result.append((record.id, name))
        return result

    date_start = fields.Date(string='Start Date')
    date_end = fields.Date(string='End Date')
    sanpham = fields.Many2one('dm.sanpham', 'Sản phẩm')
    khachhang = fields.Many2one('dm.khach', 'Khách')
    nguyenlieu = fields.Char(String='Nguyên liệu')
    tennguyenlieu = fields.Char(String='Tên nguyên liệu')
    khoiluong = fields.Float(String='Khối lượng')
    soluong = fields.Integer(String='Số lượng')
    phantram = fields.Float(String='Phần trăm')
    mathuongmaisp = fields.Char(String='Mã thương mại sp')
    tensanpham = fields.Char(String='Tên sản phẩm')
    donhang = fields.Many2one('don.hang', string='Đơn hàng')

    def get_report(self):
        if self.date_end:
            to_date = self.date_end + timedelta(days=1)
        else:
            to_date = 0

        data = {
            'model': self._name,
            'ids': self.ids,
            'form': {'date_start': self.date_start, 'date_end': self.date_end, 'to_date': to_date,
                'donhang': self.donhang.madonhang, 'sanpham': self.sanpham.id, 'khachhang': self.khachhang.id,
                'tensanpham': self.sanpham.mathuongmaisp, 'tenkhach': self.khachhang.tenkhach
            },
        }
        action = self.env.ref('mrp_fm.action_bao_cao_nhu_cau_nguyen_lieu').report_action(self, data=data)
        return action


class BaoCaoNhuCauNguyenLieu(models.AbstractModel):
    _name = 'report.mrp_fm.bao_cao_nhu_cau_nguyen_lieu_document'

    @api.model
    def _get_report_values(self, docids, data=None):
        donhang = data['form']['donhang']
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        to_date = data['form']['to_date']
        sanpham = data['form']['sanpham']
        khachhang = data['form']['khachhang']
        tensanpham = data['form']['tensanpham']
        tenkhach = data['form']['tenkhach']


        where_string = ""
        param = {}
        dieukien = 0
        if date_start:
            where_string += "where dh.ngaydat = %(date_start)s "
            param['date_start'] = date_start
            dieukien = 1

        if to_date and dieukien == 0:
            where_string += "where dh.ngaydat = %(to_date)s "
            param['to_date'] = to_date
        elif to_date and dieukien == 1:
            where_string += "And dh.ngaydat = %(to_date)s "
            param['to_date'] = to_date

        if donhang and dieukien == 0:
            where_string += "where dh.madonhang = %(donhang)s "
            param['donhang'] = donhang
        elif donhang and dieukien == 1:
            where_string += "And dh.madonhang = %(donhang)s "
            param['donhang'] = donhang

        if sanpham and dieukien == 0:
            where_string += "where dhct.mathuongmaisp = %(sanpham)s "
            param['sanpham'] = sanpham
        elif sanpham and dieukien == 1:
            where_string += "And dhct.mathuongmaisp = %(sanpham)s "
            param['sanpham'] = sanpham

        if khachhang and dieukien == 0:
            where_string += "where dh.makhach = %(khachhang)s "
            param['khachhang'] = khachhang
        elif khachhang and dieukien == 1:
            where_string += "And dh.makhach = %(khachhang)s "
            param['khachhang'] = khachhang

        query = """
                                Select  nl.manguyenlieu, nl.tennguyenlieu, SUM(dhct.soluong * ct.phantram / 100) AS khoiluong
                                from don_hang dh
                                    left join donhang_chitiet dhct ON dhct.donhang_id = dh.id
                                    left join cong_thuc ct ON ct.sanpham_ids = dhct.masx
                                    left join nguyen_lieu nl ON nl.id = ct.nguyenlieu
                                {where_string}
                                GROUP BY nl.manguyenlieu, nl.tennguyenlieu
                                """.format(where_string=where_string, )

        self.env.cr.execute(query, param)
        data_mrp = self.env.cr.fetchall()
        _ids = []

        for line in data_mrp:
            data_row = ({
                'nguyenlieu': line[0],
                'tennguyenlieu': line[1],
                'khoiluong': line[2],
            })
            _ids.append(self.env['bao.cao.nhu.cau.nguyen.lieu.wizard'].create(data_row).id)

        docs = self.env['bao.cao.nhu.cau.nguyen.lieu.wizard'].browse(_ids)
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'donhang': donhang,
            'docs': docs,
        }

