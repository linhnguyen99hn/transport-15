# -*- coding: utf-8 -*-

from odoo import models, fields, api

from datetime import datetime, timedelta

from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT


class Nhucaunguyenlieu(models.TransientModel):
    _name = 'bao.cao.nhu.cau.nguyen.lieu'
    _rec_name = 'date_start'

    date_start = fields.Date(string='Start Date')
    date_end = fields.Date(string='End Date')
    nguyenlieu = fields.Many2one('nguyen.lieu', 'Nguyên liệu')
    manguyenlieu = fields.Char('Mã nguyên liệu')
    tennguyenlieu = fields.Char('Tên nguyên liệu')
    lenhsx = fields.Char('Lệnh sx')
    donhang = fields.Char('Đơn hàng')
    ngaycapkehoach = fields.Date('Ngày cấp kế hoạch')
    khoiluongdukien = fields.Float('KL dự kiến')
    soluongkehoach = fields.Float('SL kế hoạch')
    donvitinh = fields.Char('Đvt')
    phantram = fields.Float('Phần trăm')
    def get_report(self):
        if self.date_end:
            to_date = self.date_end + timedelta(days=1)
        else:
            to_date = 0

        data = {
            'model': self._name,
            'ids': self.ids,
            'form': {
                'date_start': self.date_start, 'date_end': self.date_end, 'to_date': to_date,
                'nguyenlieu': self.nguyenlieu.manguyenlieu, 'tennguyenlieu': self.nguyenlieu.tennguyenlieu,
            },
        }

        action = self.env.ref('mrp_fm.action_bao_cao_nhu_cau_nguyen_lieu').report_action(self, data=data)
        return action

class Baocaonhucaunguyenlieu(models.AbstractModel):
    _name = 'report.mrp_fm.bao_cao_nhu_cau_nguyen_lieu_document'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        to_date = data['form']['to_date']
        nguyenlieu = data['form']['nguyenlieu']

        where_string = ""
        param = {}
        if nguyenlieu:
            where_string += "And (manguyenlieu= %(nguyenlieu)s or %(nguyenlieu)s = '' ) "
            param['nguyenlieu'] = nguyenlieu
        if date_start:
            where_string += " And (thoigian_batdau >= %(date_start)s ) "
            param['date_start'] = date_start
        if to_date:
            where_string += " And (thoigian_batdau <= %(to_date)s ) "
            param['to_date'] = to_date
        query = """
                select nl.manguyenlieu ,nl.tennguyenlieu,lsx.lenhsx, dh.madonhang as donhang, lsx.ngaycapkehoach,
                         sum(khsx.khoiluong_dukien) as khoiluongdukien
                        , ct.khoiluong/lsx.khoiluongme*sum(khsx.khoiluong_dukien) As soluongkehoach,dvt.donvitinh, ct.khoiluong
                from kehoach_sanxuat khsx
                        left join lenh_san_xuat lsx ON lsx.id = khsx.lenhsx_ids
                        LEFT JOIN cong_thuc ct ON ct.sanpham_ids=khsx.masx
                        left join nguyen_lieu nl on nl.id = ct.nguyenlieu 
                        left join don_vi_tinh dvt on dvt.id = nl.donvitinh
						left join don_hang dh ON dh.id = khsx.donhang
                where nl.manguyenlieu is not null 
                    and lsx.ngaycapkehoach is not null 
                        {where_string}
                group by nl.manguyenlieu, nl.tennguyenlieu, lsx.lenhsx, donhang, lsx.ngaycapkehoach,
                        dvt.donvitinh, ct.khoiluong, lsx.khoiluongme , dh.madonhang                                       
		""".format(where_string=where_string, )

        self.env.cr.execute(query, param)
        data_mrp_fm = self.env.cr.fetchall()
        _ids = []
        for line in data_mrp_fm:
            data_row = ({
                'manguyenlieu': line[0],
                'tennguyenlieu': line[1],
                'lenhsx': line[2],
                'donhang': line[3],
                'ngaycapkehoach': line[4],
                'khoiluongdukien': line[5],
                'soluongkehoach': line[6],
                'donvitinh': line[7],
                'phantram': line[8],
            })
            _ids.append(self.env['bao.cao.nhu.cau.nguyen.lieu'].create(data_row).id)

        docs = self.env['bao.cao.nhu.cau.nguyen.lieu'].browse(_ids)

        # data_mrp = self.env['kehoach.sanxuat'].search(domain)
        # docs = self.env['kehoach.sanxuat'].browse(data_mrp.ids)

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start,
            'date_end': date_end,
            'nguyenlieu': nguyenlieu,
            'docs': docs,
        }

