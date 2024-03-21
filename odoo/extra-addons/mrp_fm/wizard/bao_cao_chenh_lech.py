# -*- coding: utf-8 -*-

from odoo import models, fields, api

from datetime import datetime, timedelta

from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT


class Baocaochenhlech(models.TransientModel):
    _name = 'bao.cao.chenh.lech'
    _rec_name = 'date_start'

    date_start = fields.Date(string='Start Date')
    date_end = fields.Date(string='End Date')
    donhang = fields.Many2one('don.hang', 'Đơn hàng')
    sanpham = fields.Many2one('dm.sanpham', 'Sản phẩm')

    def get_report(self):
        date_start = self.date_start
        date_end = self.date_end
        domain = []

        if self.date_start:
            domain = expression.AND([domain, [('ngay', '>=', self.date_start)]])
            # date_start = date_start.strftime('%d/%m/%Y')
        if self.date_end:
            domain = expression.AND([domain, [('ngay', '<=', self.date_end)]])
            # date_end = date_end.strftime('%d/%m/%Y')
        if self.donhang:
            domain = expression.AND([domain, [('donhang', '=', self.donhang.id)]])
        if self.sanpham:
            domain = expression.AND([domain, [('sanpham', '=', self.sanpham.id)]])
        domain = expression.AND([domain, [('khoiluong_thucte', '>', 0)]])

        data = {
            'model': self._name,
            'ids': self.ids,
            'form': {
                'date_start': date_start, 'date_end': date_end, 'domain': domain, 'donhang': self.donhang,
                'sanpham': self.sanpham, 'madonhang' : self.donhang.madonhang, 'tensanpham' : self.sanpham.tensanpham,
            },
        }

        action = self.env.ref('mrp_fm.action_bao_cao_chenh_lech').report_action(self, data=data)
        return action

class Baocaodoanhso(models.AbstractModel):
    _name = 'report.mrp_fm.bao_cao_chenh_lech_document'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        sanpham = data['form']['sanpham']
        tensanpham = data['form']['tensanpham']
        donhang = data['form']['donhang']
        madonhang = data['form']['madonhang']
        domain = data['form']['domain']

        data_mrp = self.env['kehoach.sanxuat'].search(domain)
        docs = self.env['kehoach.sanxuat'].browse(data_mrp.ids)

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start,
            'date_end': date_end,
            'sanpham': sanpham,
            'tensanpham' : tensanpham,
            'donhang': donhang,
            'madonhang': madonhang,
            'docs': docs,
        }

