# -*- coding: utf-8 -*-

from odoo import models, fields, api

from datetime import datetime, timedelta

from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT


class SaleBackorderWizard(models.TransientModel):
    _name = 'bao.cao.hieu.qua'

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
    donhang = fields.Many2one('don.hang', 'Đơn hàng')
    lenhsx = fields.Many2one("lenh.san.xuat", "Lệnh sản xuất")
    masx = fields.Many2one('cong.thuc.phoi.tron', 'Mã sản xuất',)
    mathuongmai = fields.Many2one('dm.sanpham', 'Mã thương mại')
    kl_dukien = fields.Float('Khối lượng dự kiến')
    kl_thucte = fields.Float('Khối lượng thực tế')
    tg_dukien = fields.Float('Thời gian dự kiến')
    tg_thucte = fields.Float('Thời gian thực tế')

    def get_report(self):
        if self.date_end:
            to_date = self.date_end + timedelta(days=1)
        else:
            to_date = 0

        data = {
            'model': self._name,
            'ids': self.ids,
            'form': {'date_start': self.date_start, 'date_end': self.date_end, 'to_date': to_date,
                'donhang': self.donhang.id, 'madonhang': self.donhang.madonhang,
                'lenhsx': self.lenhsx.id, 'malenhsx': self.lenhsx.lenhsx,
                'masx': self.masx.id, 'tenmasx': self.masx.tencongthuc,

            },
        }

        action = self.env.ref('mrp_fm.action_bao_cao_hieu_qua_sx').report_action(self, data=data)
        return action


class ReportSaleBackorder(models.AbstractModel):
    _name = 'report.mrp_fm.bao_cao_hieu_qua_sx_document'

    @api.model
    def _get_report_values(self, docids, data=None):
        to_date = data['form']['to_date']
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        donhang = data['form']['donhang']
        madonhang = data['form']['madonhang']
        lenhsx = data['form']['lenhsx']
        malenhsx = data['form']['malenhsx']
        masx = data['form']['masx']
        tenmasx = data['form']['tenmasx']

        where_string = ""
        param = {}
        if donhang:
            where_string += "And (donhang= %(donhang)s ) "
            param['donhang'] = donhang
        if lenhsx:
            where_string += " And (lenhsx_ids= %(lenhsx)s ) "
            param['lenhsx'] = lenhsx
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
                        SELECT lenhsx_ids, donhang, sanpham, masx, 
		                        sum(khoiluong_dukien) As kl_dukien, sum(khoiluong_thucte) As kl_thucte,
		                        sum(thoigian_dukien) As tg_dukien, sum(thoigian_chaymay_thucte) As tg_thucte
                        from kehoach_sanxuat 
                        where khoiluong_thucte > 0 {where_string}
                        GROUP by lenhsx_ids, donhang, masx, sanpham

                        """.format(where_string=where_string, )

        self.env.cr.execute(query, param)
        data_mrp_fm = self.env.cr.fetchall()
        _ids = []
        for line in data_mrp_fm:
            data_row = ({
                'lenhsx': line[0],
                'donhang': line[1],
                'mathuongmai': line[2],
                'masx': line[3],
                'kl_dukien': line[4],
                'kl_thucte': line[5],
                'tg_dukien': line[6],
                'tg_thucte': line[7],

            })
            _ids.append(self.env['bao.cao.hieu.qua'].create(data_row).id)

        docs = self.env['bao.cao.hieu.qua'].browse(_ids)

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start,
            'date_end': date_end,
            'madonhang': madonhang,
            'malenhsx': malenhsx,
            'tenmasx': tenmasx,
            'docs': docs,
        }
