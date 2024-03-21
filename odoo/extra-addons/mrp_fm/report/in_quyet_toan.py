# -*- coding: utf-8 -*-

from odoo import models, fields, api

from datetime import datetime, timedelta

from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT


class InquyettoanrWizard(models.TransientModel):
    _name = 'in.quyet.toan.wizard'

    # _rec_name = 'date_start'
    @api.depends('create_date')
    def name_get(self):
        result = []
        for record in self:
            name = record.create_date.strftime('%d-%m-%Y')
            result.append((record.id, name))
        return result

    lenhsx = fields.Many2one('lenh.san.xuat', 'Lệnh sản xuất số', required=True)
    masx = fields.Many2one('cong.thuc.phoi.tron', 'Mã sản xuất')
    khoiluongthanhpham = fields.Float('Khối lượng (KG)')
    phe = fields.Float('Phế')
    banthanhpham = fields.Float('Bán thành phẩm')
    haophi = fields.Float('Khối lượng hao phí', store=True)

    def get_report(self):

        data = {
            'model': self._name,
            'ids': self.ids,
            'form': {
                'malenhsx': self.lenhsx.id, 'lenhsx': self.lenhsx.lenhsx, 'tongcapnguyenlieu': self.lenhsx.tongnguyenlieucap,
                'matem': self.lenhsx.matemsp, 'somesx': self.lenhsx.tongmesx, 'tptheoycsx': self.lenhsx.tptheoycsx,
                'bophanxuat': self.lenhsx.bophanxuat, 'bophannhap': self.lenhsx.bophannhap, 'lydoxuat': self.lenhsx.lydoxuat,
                'ngaycapkehoach': self.lenhsx.ngaycapkehoach, 'ngaycapthucte': self.lenhsx.ngaycapthucte
            },
        }

        action = self.env.ref('mrp_fm.in_quyet_toan').report_action(self, data=data)
        return action

class LenhSanXuat(models.AbstractModel):
    _name = 'report.mrp_fm.in_quyet_toan_document'

    @api.model
    def _get_report_values(self, docids, data=None):
        lenhsx = data['form']['lenhsx']
        malenhsx = data['form']['malenhsx']
        tongcapnguyenlieu = data['form']['tongcapnguyenlieu']
        matem = data['form']['matem']
        somesx = data['form']['somesx']
        tptheoycsx = data['form']['tptheoycsx']
        bophanxuat = data['form']['bophanxuat']
        bophannhap = data['form']['bophannhap']
        lydoxuat = data['form']['lydoxuat']
        ngaycapkehoach = data['form']['ngaycapkehoach']
        ngaycapthucte = data['form']['ngaycapthucte']

        masx = self.env['kehoach.sanxuat'].search([('lenhsx_ids', '=', malenhsx)], limit=1).masx
        manoibo = self.env['cong.thuc.phoi.tron'].search([('id', '=', masx.id)]).tencongthuc

        param = {}
        param['lenhsx'] = malenhsx
        query = """
                        SELECT sum(kh.khoiluong_thucte) As thanhpham, sum(kh.ban_thanh_pham)  As banthanhpham,
                                sum(kh.phe) As phe, sum(kh.hao_phi) As haophi
                        from  lenh_san_xuat lsx 
                        left join kehoach_sanxuat kh on kh.lenhsx_ids = lsx.id
                        where lsx.id = %(lenhsx)s
                        """
        self.env.cr.execute(query, param)
        data_dinhmuc = self.env.cr.fetchall()
        _ids = []
        for line in data_dinhmuc:
            data_row = ({
                'khoiluongthanhpham': line[0],
                'banthanhpham': line[1],
                'phe': line[2],
                'haophi': line[3],
                'lenhsx': malenhsx,
            })
            _ids.append(self.env['in.quyet.toan.wizard'].create(data_row).id)

        docs = self.env['in.quyet.toan.wizard'].browse(_ids)



        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'lenhsx': lenhsx,
            'manoibo': manoibo,
            'tongcapnguyenlieu': tongcapnguyenlieu,
            'matem': matem,
            'somesx': somesx,
            'tptheoycsx': tptheoycsx,
            'bophanxuat': bophanxuat,
            'bophannhap': bophannhap,
            'lydoxuat': lydoxuat,
            'ngaycapkehoach': ngaycapkehoach,
            'ngaycapthucte': ngaycapthucte,
            'docs': docs,
        }
