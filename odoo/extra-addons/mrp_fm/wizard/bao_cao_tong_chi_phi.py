# -*- coding: utf-8 -*-

from odoo import models, fields, api

from datetime import datetime, timedelta

from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT


class Baocaotongchiphi(models.TransientModel):
    _name = 'bao.cao.tong.chi.phi'
    _rec_name = "manguyenlieu"
    _order = 'dongia desc, soluong desc, thanhtien DESC'

    @api.depends('create_date')
    def name_get(self):
        result = []
        for record in self:
            name = record.create_date.strftime('%d-%m-%Y')
            result.append((record.id, name))
        return result

    date_start = fields.Date(string='Từ ngày', required=True)
    date_end = fields.Date(string='Đến ngày', required=True)
    manguyenlieu = fields.Char('Mã nguyên liệu')
    nguyenlieu = fields.Char('Nguyên liệu')
    thanhtien = fields.Float('Thành tiền')
    donvitinh = fields.Char("Đơn vị tính")
    dongia = fields.Float("Đơn giá")
    soluong = fields.Float("Số lượng")

    def get_report(self):
        date_start = self.date_start
        date_end = self.date_end

        date_start = date_start.strftime('%d/%m/%Y')
        date_end = date_end.strftime('%d/%m/%Y')

        data = {
            'model': self._name,
            'ids': self.ids,
            'form': {
                'date_start': self.date_start, 'date_end': self.date_end, 'tungay': date_start, 'denngay': date_end
            },
        }

        action = self.env.ref('mrp_fm.bao_cao_tong_chi_phi').report_action(self, data=data)
        return action


class Baocaochiphi(models.AbstractModel):
    _name = 'report.mrp_fm.bao_cao_tong_chi_phi_document'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        tungay = data['form']['tungay']
        denngay = data['form']['denngay']

        param = {}
        where_string = ""
        if date_start:
            where_string += "And (dhct.ngaydat >= %(date_start)s ) "
            param['date_start'] = date_start
        if date_end:
            where_string += "And (dhct.ngaydat <= %(date_end)s ) "
            param['date_end'] = date_end

        query = """
                        SELECT nl.manguyenlieu, nl.tennguyenlieu, dvt.donvitinh, gnl.dongia
                                , sum(ct.phantram * dhct.soluong * ( 1 + (CASE
                                    WHEN dhct.soluong < 25000 THEN 0.008
                                    WHEN 25000 <= dhct.soluong and dhct.soluong <= 100000 THEN 0.0065
                                    WHEN dhct.soluong > 100000 THEN 0.005
                                    WHEN khsx.kh_may_id = 4 THEN 0.007
                                END)) / 100) as soluong
                                , sum(ct.phantram * dhct.soluong * ( 1 + (CASE
                                    WHEN dhct.soluong < 25000 THEN 0.008
                                    WHEN 25000 <= dhct.soluong and dhct.soluong <= 100000 THEN 0.0065
                                    WHEN dhct.soluong > 100000 THEN 0.005
                                    WHEN khsx.kh_may_id = 4 THEN 0.007
                                END)) * gnl.dongia / 100) as chiphi
                        From donhang_chitiet dhct
                            Left join (Select distinct donhangchitiet_id, kh_may_id From kehoach_sanxuat) khsx ON khsx.donhangchitiet_id = dhct.id
                            Left join don_hang dh On dhct.donhang_id = dh.id
                            Left join dm_sanpham sp On dhct.mathuongmaisp = sp.id
                            Left join cong_thuc_phoi_tron ctpt On sp.manoibosp = ctpt.id
                            Left join cong_thuc ct On ct.sanpham_ids = ctpt.id
                            Left join gia_nguyen_lieu gnl ON ct.nguyenlieu = gnl.nguyenlieu and gnl.bang_gia_ids = dh.banggia
                            Left join nguyen_lieu nl ON ct.nguyenlieu = nl.id
                            Left join don_vi_tinh dvt On nl.donvitinh = dvt.id
                        where dh.banggia is not null and dhct.soluong is not null {where_string}
                        Group by nl.manguyenlieu, nl.tennguyenlieu,nl.donvitinh,ctpt.dongia, dhct.soluong, dvt.donvitinh, gnl.dongia 
                        """.format(where_string=where_string)
        #LEFT JOIN bang_gia_hieu_luc({date_start}) gnl ON ct.nguyenlieu = gnl.nguyenlieu
        #, date_start=date_start)

        self.env.cr.execute(query, param)
        data_chiphi = self.env.cr.fetchall()
        _ids = []
        for line in data_chiphi:
            data_row = ({
                'manguyenlieu': line[0],
                'nguyenlieu': line[1],
                'donvitinh': line[2],
                'dongia': line[3],
                'soluong': line[4],
                'thanhtien': line[5],
                'date_start': date_start,
                'date_end': date_end,
            })
            _ids.append(self.env['bao.cao.tong.chi.phi'].create(data_row).id)

        docs = self.env['bao.cao.tong.chi.phi'].browse(_ids)

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'tungay': tungay,
            'denngay': denngay,
            'docs': docs,
        }
