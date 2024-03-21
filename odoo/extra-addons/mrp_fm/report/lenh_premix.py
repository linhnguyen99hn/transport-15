# -*- coding: utf-8 -*-

from odoo import models, fields, api

from datetime import datetime, timedelta

from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT


class Lenhpremix(models.TransientModel):
    _name = 'lenh.premix.wizard'

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
    khoiluong = fields.Float('Khối lượng')
    khoiluongme = fields.Float('Khối lượng(kg)/Mẻ')
    nhua = fields.Boolean('Nhựa')
    sobaonguyen = fields.Integer('Số bao nguyên')
    stt = fields.Integer('Số thứ tự')
    premix = fields.Char('Premix')

    def get_report(self):
        data = {
            'model': self._name,
            'ids': self.ids,
            'form': {
                'malenhsx': self.lenhsx.id, 'lenhsx': self.lenhsx.lenhsx, 'tongsome': self.lenhsx.tongmesx,
                'khoiluongme': self.lenhsx.khoiluongme, 'mamay': self.lenhsx.may_id.mamay, 'tongnguyenlieucap': self.lenhsx.tongnguyenlieucap,
                'chaylai': self.lenhsx.chaylai, 'thanhphamchaylai': self.lenhsx.thanhphamchaylai,
                'khoiluong1mechaylai': self.lenhsx.khoiluong1mechaylai

            },
        }

        action = self.env.ref('mrp_fm.lenh_premix').report_action(self, data=data)
        return action


class ReportLenhPremix(models.AbstractModel):
    _name = 'report.mrp_fm.lenh_premix_document'

    @api.model
    def _get_report_values(self, docids, data=None):
        malenhsx = data['form']['malenhsx']
        lenhsx = data['form']['lenhsx']
        tongsome = data['form']['tongsome']
        khoiluongme = data['form']['khoiluongme']
        tongnguyenlieucap = data['form']['tongnguyenlieucap']
        mamay = data['form']['mamay']
        masp = self.env['kehoach.sanxuat'].search([('lenhsx_ids', '=', malenhsx)], limit=1).sanpham.id
        tensp = self.env['dm.sanpham'].search([('id', '=', masp)], limit=1).tensanpham
        thanhphamchaylai = data['form']['thanhphamchaylai']
        khoiluong1mechaylai = data['form']['khoiluong1mechaylai']
        chaylai = data['form']['chaylai']

        param = {}
        param['lenhsx'] = malenhsx

        query3 = """
                                        SELECT nl.tennguyenlieu, dvt.donvitinh, sum(khsx.khoiluong_dukien)
                                               , ct.khoiluong/lsx.khoiluongme*sum(khsx.khoiluong_dukien) As soluongkehoach
                                              , ct.khoiluong As khoiluongnguyenlieu1me, ct.khoiluong, nl.nhua
                                              ,FLOOR(ct.khoiluong / 25) As sobaonguyen
                                              , nl.manguyenlieu, ct.id 
                                              , ctpt.premix, ct.sothutu
                                        from lenh_san_xuat lsx
                                               LEFT JOIN kehoach_sanxuat khsx ON khsx.lenhsx_ids = lsx.id
                                               LEFT JOIN cong_thuc ct ON ct.sanpham_ids=khsx.masx
                                               left join nguyen_lieu nl on nl.id = ct.nguyenlieu 
                							   left join nhom_nguyen_lieu nnl on nnl.id = nl.nhomnguyenlieu
                							   left join nhom_nguyen_lieu nnlc on nnlc.id=nnl.nhomcha
                                               left join don_vi_tinh dvt on dvt.id = nl.donvitinh
                                               LEFT JOIN cong_thuc_phoi_tron ctpt on ctpt.id = khsx.masx

                                        where khsx.lenhsx_ids = %(lenhsx)s and nnlc.manhom = 'PREMIX'
                                        group by  nl.tennguyenlieu, dvt.donvitinh, ct.id, lsx.khoiluongme, nl.nhua, nl.manguyenlieu
                                                    , ctpt.premix, ct.sothutu
                                        UNION ALL
                                        SELECT nl.tennguyenlieu, dvt.donvitinh, sum(khsx.khoiluong_dukien)
                                               , ct.khoiluong/lsx.khoiluongme*sum(khsx.khoiluong_dukien) As soluongkehoach
                                              , ct.khoiluong As khoiluongnguyenlieu1me, ct.khoiluong, nl.nhua
                                              ,FLOOR(ct.khoiluong / 25) As sobaonguyen 
                                              , nl.manguyenlieu, ct.id
                                              , ctpt.premix, ct.sothutu
                                        from lenh_san_xuat lsx
                                               LEFT JOIN kehoach_sanxuat khsx ON khsx.lenhsx_ids = lsx.id
                                               LEFT JOIN cong_thuc ct ON ct.sanpham_ids=khsx.masx
                                               left join nguyen_lieu nl on nl.id = ct.nguyenlieu 
                							   left join nhom_nguyen_lieu nnl on nnl.id = nl.nhomnguyenlieu
                							   left join nhom_nguyen_lieu nnlc on nnlc.id=nnl.nhomcha
                                               left join don_vi_tinh dvt on dvt.id = nl.donvitinh
                                               LEFT JOIN cong_thuc_phoi_tron ctpt on ctpt.id = khsx.masx
                                        where khsx.lenhsx_ids = %(lenhsx)s and nnlc.manhom = 'NGUYENLIEU' and nl.nhua = True
                                        group by  nl.tennguyenlieu, dvt.donvitinh, ct.id, lsx.khoiluongme, nl.nhua, nl.manguyenlieu
                                                    , ctpt.premix, ct.sothutu
                                        order by id
                                        """
        self.env.cr.execute(query3, param)
        data_premix = self.env.cr.fetchall()
        _ids = []
        for line in data_premix:
            data_row = ({
                'tennguyenlieu': line[0],
                'khoiluongme': line[4],
                'khoiluong': line[5],
                'nhua': line[6],
                'sobaonguyen': line[7],
                'manguyenlieu': line[8],
                'premix': line[10],
                'stt': line[11],

                'lenhsx': malenhsx,
            })
            _ids.append(self.env['lenh.premix.wizard'].create(data_row).id)

        docs3 = self.env['lenh.premix.wizard'].browse(_ids)

        settings = self.env['ir.config_parameter']
        parameters = {
            'tphtkh': settings.get_param('MrpFm.tphtkh', default=''),
            'tpsanxuat': settings.get_param('MrpFm.tpsanxuat', default=''),
            'gdcongnghe': settings.get_param('MrpFm.gdcongnghe', default=''),
            'tonggiamdoc': settings.get_param('MrpFm.tonggiamdoc', default=''),
            'tttsanxuat': settings.get_param('MrpFm.tttsanxuat', default=''),
            'ketoan': settings.get_param('MrpFm.ketoan', default=''),
            'ttpremix': settings.get_param('MrpFm.ttpremix', default=''),
            'psale': settings.get_param('MrpFm.psale', default=''),
            'bophandonggoi': settings.get_param('MrpFm.bophandonggoi', default=''),
            'bophanhoanthien': settings.get_param('MrpFm.bophanhoanthien', default=''),
            'truongcasx': settings.get_param('MrpFm.truongcasx', default=''),
            'gdsanxuat': settings.get_param('MrpFm.gdsanxuat', default=''),
            'tentonggiamdoc': settings.get_param('MrpFm.tentonggiamdoc', default=''),
            'tentpsanxuat': settings.get_param('MrpFm.tentpsanxuat', default=''),
            'tenttpremix': settings.get_param('MrpFm.tenttpremix', default=''),
            'tengdcongnghe': settings.get_param('MrpFm.tengdcongnghe', default=''),
            'tenketoan': settings.get_param('MrpFm.tenketoan', default=''),
            'tengdsanxuat': settings.get_param('MrpFm.tengdsanxuat', default=''),
            'tennguoilap': settings.get_param('MrpFm.tennguoilap', default=''),
        }

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'lenhsx': lenhsx,
            'tongsome': tongsome,
            'khoiluongme': khoiluongme,
            'tongnguyenlieucap': tongnguyenlieucap,
            'thanhphamchaylai': thanhphamchaylai,
            'khoiluong1mechaylai': khoiluong1mechaylai,
            'chaylai': chaylai,
            'mamay': mamay,
            'masp': masp,
            'tensp': tensp,
            'docs': docs3,
            'parameters': parameters,
        }
