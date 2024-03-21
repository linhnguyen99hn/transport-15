# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Baocaonguyenlieuxuat(models.TransientModel):
    _name = 'bao.cao.nguyen.lieu.xuat'

    # _rec_name = 'date_start'
    @api.depends('create_date')
    def name_get(self):
        result = []
        for record in self:
            name = record.create_date.strftime('%d-%m-%Y')
            result.append((record.id, name))
        return result

    date_start = fields.Date(string='Start Date', required=True)
    date_end = fields.Date(string='End Date', required=True)
    nguyenlieu_ids = fields.Many2one('nguyen.lieu', 'Nguyên liệu')
    manguyenlieu = fields.Char('Mã nguyên liệu')
    nguyenlieu = fields.Char('Nguyên liệu')
    khoiluong = fields.Float('Khối lượng')
    donvitinh = fields.Char("Dơn vị tính")

    def get_report(self):
        if self.date_start:
            tungay = self.date_start.strftime('%d/%m/%Y')
        if self.date_end:
            dengay = self.date_end.strftime('%d/%m/%Y')
        data = {
            'model': self._name,
            'ids': self.ids,
            'form': {
                'date_start': self.date_start, 'date_end': self.date_end, 'nguyenlieu_ids': self.nguyenlieu_ids.id,
                'tennguyenlieu': self.nguyenlieu_ids.tennguyenlieu, 'tungay': tungay, 'denngay': dengay
            },
        }

        action = self.env.ref('mrp_fm.action_bao_cao_nguyen_lieu_xuat').report_action(self, data=data)
        return action


class LenhSanXuat(models.AbstractModel):
    _name = 'report.mrp_fm.bao_cao_nguyen_lieu_xuat_document'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        tungay = data['form']['tungay']
        denngay = data['form']['denngay']
        nguyenlieu_ids = data['form']['nguyenlieu_ids']
        tennguyenlieu = data['form']['tennguyenlieu']

        param = {}
        where_string = ""

        x = 0
        if date_start:
            where_string += " Where (khsx.ngay >= %(date_start)s ) "
            param['date_start'] = date_start
            x = 1

        if date_end and x == 1:
            where_string += " And (khsx.ngay <= %(date_end)s ) "
            param['date_end'] = date_end
        elif date_end and x == 0:
            where_string += " Where (khsx.ngay <= %(date_end)s ) "
            param['date_end'] = date_end
            x = 1

        if nguyenlieu_ids and x == 1:
            where_string += " And (nl.id = %(nguyenlieu_ids)s ) "
            param['nguyenlieu_ids'] = nguyenlieu_ids
        elif nguyenlieu_ids and x == 0:
            where_string += " Where (nl.id = %(nguyenlieu_ids)s ) "
            param['nguyenlieu_ids'] = nguyenlieu_ids

        query = """
                    SELECT distinct nl.manguyenlieu, nl.tennguyenlieu, dvt.donvitinh
                            , SUM(khoiluong * lsx.tongmesx) As khoiluongnguyenlieu
                    From lenh_san_xuat lsx
                      LEFT JOIN kehoach_sanxuat khsx ON khsx.lenhsx_ids = lsx.id
                      LEFT JOIN cong_thuc ct ON ct.sanpham_ids = khsx.masx
                      left join nguyen_lieu nl on nl.id = ct.nguyenlieu
                      left join don_vi_tinh dvt on nl.donvitinh = dvt.id
                    {where_string}
                    Group by nl.id, ct.nguyenlieu, nl.manguyenlieu, nl.tennguyenlieu ,dvt.donvitinh order by  khoiluongnguyenlieu desc 
                        """.format(where_string=where_string, )
        self.env.cr.execute(query, param)
        data_rp = self.env.cr.fetchall()
        _ids = []
        for line in data_rp:
            data_row = ({
                'manguyenlieu': line[0],
                'nguyenlieu': line[1],
                'donvitinh': (line[2]),
                'khoiluong': line[3],
                'date_start': date_start,
                'date_end': date_end
            })
            _ids.append(self.env['bao.cao.nguyen.lieu.xuat'].create(data_row).id)

        docs = self.env['bao.cao.nguyen.lieu.xuat'].browse(_ids)

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start,
            'date_end': date_end,
            'tungay': tungay,
            'denngay': denngay,
            'tennguyenlieu': tennguyenlieu,
            'docs': docs,
        }
