# -*- coding: utf-8 -*-

from odoo import models, fields, api

from datetime import datetime, timedelta

from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT


class Baocaochenhlech(models.TransientModel):
    _name = 'bao.cao.ket.qua'
    _rec_name = 'date_start'

    date_start = fields.Date(string='Start Date')
    date_end = fields.Date(string='End Date')
    khachhang = fields.Many2one('dm.khach', 'Khách hàng')
    # donhang = fields.Many2one('don.hang', 'Đơn hàng', domain="[('makhach', '=?', id)]")
    donhang = fields.Many2one('don.hang', 'Đơn hàng')
    donhangchitiet_id = fields.Many2one('donhang.chitiet', 'Sản phẩm', domain="[('donhang_id', '=?', donhang)]")

    madonhang = fields.Char('Mã đơn hàng')
    tensanpham = fields.Char('Tên sản phẩm')
    may = fields.Char('Máy')
    ngay = fields.Date(string='Ngày')
    lenhsx = fields.Many2one("lenh.san.xuat",  "Lệnh sản xuất")
    masx = fields.Char('Mã sản xuất')
    mathuongmai = fields.Char('Mã thương mại')
    kl_dukien = fields.Float('Khối lượng dự kiến')
    kl_thucte = fields.Float('Khối lượng thực tế')
    tg_dukien = fields.Float('Thời gian dự kiến')
    tg_thucte = fields.Float('Thời gian thực tế')
    hieusuat = fields.Float('Hiệu suất')
    chenhlech = fields.Float('Chênh lệch')
    slbinhquan = fields.Float('Sản lượng bình quân')
    sanluong = fields.Float('Sản lượng')

    def get_report(self):

        if self.date_end:
            to_date = self.date_end + timedelta(days=1)
        else:
            to_date = 0

        data = {
            'model': self._name,
            'ids': self.ids,
            'form': {
                'date_start': self.date_start, 'date_end': self.date_end, 'donhang': self.donhang.madonhang, 'to_date': to_date,
                'sanpham': self.donhangchitiet_id.mathuongmaisp.mathuongmaisp , 'madonhang': self.donhang.madonhang, 'khachhang': self.khachhang.makhach
            },
        }

        action = self.env.ref('mrp_fm.action_bao_cao_ket_qua_sx').report_action(self, data=data)
        return action


class Baocaodoanhso(models.AbstractModel):
    _name = 'report.mrp_fm.bao_cao_ket_qua_sx_document'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        to_date = data['form']['to_date']
        sanpham = data['form']['sanpham']
        donhang = data['form']['donhang']
        khachhang = data['form']['khachhang']

        where_string = ""
        param = {}
        if khachhang:
            where_string += "And (kh.makhach = %(khachhang)s ) "
            param['khachhang'] = khachhang
        if donhang:
            where_string += "And (dh.madonhang = %(donhang)s ) "
            param['donhang'] = donhang
        if sanpham:
            where_string += " And (sp.mathuongmaisp= %(sanpham)s ) "
            param['sanpham'] = sanpham
        # if masx:
        #     where_string += " And (masx = %(masx)s ) "
        #     param['masx'] = masx
        if date_start:
            where_string += " And (thoigian_batdau_thucte >= %(date_start)s ) "
            param['date_start'] = date_start
        if to_date:
            where_string += " And (thoigian_batdau_thucte <= %(to_date)s ) "
            param['to_date'] = to_date
        query = """
                        SELECT ngay, lenhsx_ids as lenhsx,may.mamay as may,  dh.madonhang as donhang, ctpt.tencongthuc masx, sp.mathuongmaisp as mathuongmai,
								sp.tensanpham as tensanpham,
		                        sum(khoiluong_dukien) As kl_dukien, sum(khoiluong_thucte) As kl_thucte,
								sum(khoiluong_thucte)-sum(khoiluong_dukien) as chenhlech,
								sum(khoiluong_thucte)/sum(khoiluong_dukien)*100 as hieusuat,
								sum(khoiluong_thucte)/22 as SLbinhquan,
		                        sum(thoigian_dukien) As tg_dukien, sum(thoigian_chaymay_thucte) As tg_thucte
                        from kehoach_sanxuat khsx
							left join dm_may may ON may.id = khsx.kh_may_id
							left join dm_sanpham sp ON sp.id = khsx.sanpham
							left join don_hang dh ON dh.id = khsx.donhang
                            left join dm_khach kh ON kh.id = dh.makhach
                            left join cong_thuc_phoi_tron ctpt ON ctpt.id = khsx.masx
                                where khoiluong_thucte > 0 {where_string}
                        GROUP by ngay, lenhsx_ids, may.mamay, donhang, masx,sp.mathuongmaisp, sp.tensanpham, sanpham, dh.madonhang, ctpt.tencongthuc
                                """.format(where_string=where_string, )

        self.env.cr.execute(query, param)
        data_mrp_fm = self.env.cr.fetchall()
        _ids = []
        for line in data_mrp_fm:
            data_row = ({
                'ngay': line[0],
                'lenhsx': line[1],
                'may': line[2],
                'madonhang': line[3],
                'masx': line[4],
                'mathuongmai': line[5],
                'tensanpham': line[6],
                'kl_dukien': line[7],
                'kl_thucte': line[8],
                'chenhlech': line[9],
                'hieusuat': line[10],
                'slbinhquan': line[11],
                'tg_dukien': line[12],
                'tg_thucte': line[13],
            })
            _ids.append(self.env['bao.cao.ket.qua'].create(data_row).id)

        docs = self.env['bao.cao.ket.qua'].browse(_ids)

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start,
            'date_end': date_end,
            'sanpham': sanpham,
            'donhang': donhang,
            'khachhang': khachhang,
            'docs': docs,
        }
