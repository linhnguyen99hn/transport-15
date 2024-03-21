# -*- coding: utf-8 -*-

from odoo import models, fields, api

from datetime import datetime, timedelta

from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT


class QuycachdonggoivahoanthienWizard(models.TransientModel):
    _name = 'quy.cach.dong.goi.va.hoan.thien.wizard'

    # _rec_name = 'date_start'
    @api.depends('create_date')
    def name_get(self):
        result = []
        for record in self:
            name = record.create_date.strftime('%d-%m-%Y')
            result.append((record.id, name))
        return result

    lenhsx = fields.Many2one('lenh.san.xuat', 'Lệnh sản xuất số', required=True)
    may = fields.Many2one('dm.may', 'Máy')
    masx = fields.Many2one('cong.thuc.phoi.tron', 'Mã sản xuất')
    tptheoycsx = fields.Many2one('lenh.san.xuat', 'TP theo YCSX')

    tenquycach = fields.Char('Tên quy cách')
    maquycach = fields.Text('Mô tả')
    khoiluongnvl1me = fields.Float('Khối lượng (KG)')

    def get_report(self):

        data = {
            'model': self._name,
            'ids': self.ids,
            'form': {
                'malenhsx': self.lenhsx.id, 'lenhsx': self.lenhsx.lenhsx, 'mamay': self.lenhsx.may_id.mamay,
                'tptheoycsx':self.lenhsx.tptheoycsx, 'haohut': self.lenhsx.haohut, 'soluongme': self.lenhsx.tongmesx,
                'chaylai': self.lenhsx.chaylai, 'khoiluong1mechaylai': self.lenhsx.khoiluong1mechaylai
            },
        }

        action = self.env.ref('mrp_fm.quy_cach_dong_goi_va_hoan_thien').report_action(self, data=data)
        return action

class QuyCachDongGoiVaHoanThien(models.AbstractModel):
    _name = 'report.mrp_fm.quy_cach_dong_goi_va_hoan_thien_document'

    @api.model
    def _get_report_values(self, docids, data=None):
        lenhsx = data['form']['lenhsx']
        malenhsx = data['form']['malenhsx']
        mamay = data['form']['mamay']
        masx = self.env['kehoach.sanxuat'].search([('lenhsx_ids', '=', malenhsx)], limit=1).masx
        manoibo = self.env['cong.thuc.phoi.tron'].search([('id', '=', masx.id)]).tencongthuc
        tptheoycsx = data['form']['tptheoycsx']
        haohut = data['form']['haohut']
        soluongme = data['form']['soluongme']
        khoiluong1mechaylai = data['form']['khoiluong1mechaylai']
        chaylai = data['form']['chaylai']


        param = {}
        param['lenhsx'] = malenhsx

        query1 = """
                                SELECT nl.manguyenlieu, ct.nguyenlieu , ct.khoiluong, sum(khsx.khoiluong_dukien)
                                       , ct.khoiluong/lsx.khoiluongme*sum(khsx.khoiluong_dukien) As khoiluongnguyenlieu
                                       , ct.khoiluong As khoiluongnguyenlieu1me
                                from lenh_san_xuat lsx
                                       LEFT JOIN kehoach_sanxuat khsx ON khsx.lenhsx_ids = lsx.id
                                       LEFT JOIN cong_thuc ct ON ct.sanpham_ids = khsx.masx
                                        left join nguyen_lieu nl on nl.id = ct.nguyenlieu 

                                where khsx.lenhsx_ids = %(lenhsx)s
                                group by ct.nguyenlieu,  nl.manguyenlieu, ct.khoiluong, ct.id, lsx.khoiluongme ,nl.id
                                order by ct.id
                                """
        self.env.cr.execute(query1, param)
        data_dinhmuc = self.env.cr.fetchall()
        _ids = []
        for line in data_dinhmuc:
            data_row = ({
                'khoiluongnvl1me': line[5],
                'lenhsx': malenhsx,
            })
            _ids.append(self.env['lenh.sx.wizard'].create(data_row).id)

        docs1 = self.env['lenh.sx.wizard'].browse(_ids)

        query2 = """
                               SELECT dmqc.tenquycach, dmqc.mota 
                               from lenh_san_xuat lsx
                                        LEFT JOIN kehoach_sanxuat khsx ON khsx.lenhsx_ids = lsx.id
                                        LEFT JOIN donhang_chitiet dhct ON dhct.id = khsx.donhangchitiet_id
                                        LEFT JOIN dm_sanpham sp ON sp.Id = dhct.mathuongmaisp
                                        LEFT JOIN quycach_sanpham qc ON qc.sanpham_id = sp.id
                                        LEFT JOIN dm_quycach dmqc ON qc.quycach_id = dmqc.id
                                where khsx.lenhsx_ids = %(lenhsx)s
                                group by dmqc.tenquycach, dmqc.mota
                                """

        self.env.cr.execute(query2, param)
        data_quycach = self.env.cr.fetchall()
        _ids = []
        for line in data_quycach:
            data_row = ({
                'maquycach': line[0],
                'tenquycach': line[1],
                'lenhsx': malenhsx,
            })
            _ids.append(self.env['lenh.sx.wizard'].create(data_row).id)

        docs2 = self.env['lenh.sx.wizard'].browse(_ids)

        settings = self.env['ir.config_parameter']
        parameters = {
            'tphtkh': settings.get_param('MrpFm.tphtkh', default=''),
            'tpsanxuat': settings.get_param('MrpFm.tpsanxuat', default=''),
            'gdcongnghe': settings.get_param('MrpFm.gdcongnghe', default=''),
            'tpcongnghe': settings.get_param('MrpFm.tpcongnghe', default=''),
            'tonggiamdoc': settings.get_param('MrpFm.tonggiamdoc', default=''),
            'tttsanxuat': settings.get_param('MrpFm.tttsanxuat', default=''),
            'ketoan': settings.get_param('MrpFm.ketoan', default=''),
            'ttpremix': settings.get_param('MrpFm.ttpremix', default=''),
            'psale': settings.get_param('MrpFm.psale', default=''),
            'bophandonggoi': settings.get_param('MrpFm.bophandonggoi', default=''),
            'bophanhoanthien': settings.get_param('MrpFm.bophanhoanthien', default=''),
            'truongcasx': settings.get_param('MrpFm.truongcasx', default=''),
            'gdsanxuat': settings.get_param('MrpFm.gdsanxuat', default=''),
            'tentphtkh': settings.get_param('MrpFm.tentphtkh', default=''),
            'tentpsanxuat': settings.get_param('MrpFm.tentpsanxuat', default=''),
            'tengdcongnghe': settings.get_param('MrpFm.tengdcongnghe', default=''),
            'tentpcongnghe': settings.get_param('MrpFm.tentpcongnghe', default=''),
            'tentonggiamdoc': settings.get_param('MrpFm.tentonggiamdoc', default=''),
            'tentttsanxuat': settings.get_param('MrpFm.tentttsanxuat', default=''),
            'tenketoan': settings.get_param('MrpFm.tenketoan', default=''),
            'tenttpremix': settings.get_param('MrpFm.tenttpremix', default=''),
            'tenphongsale': settings.get_param('MrpFm.tenphongsale', default=''),
            'tenbophandonggoi': settings.get_param('MrpFm.tenbophandonggoi', default=''),
            'tenbophanhoanthien': settings.get_param('MrpFm.tenbophanhoanthien', default=''),
            'tentruongcasx': settings.get_param('MrpFm.tentruongcasx', default=''),
            'tengdsanxuat': settings.get_param('MrpFm.tengdsanxuat', default=''),
        }

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'mamay': mamay,
            'manoibo': manoibo,
            'tptheoycsx': tptheoycsx,
            'haohut': haohut,
            'soluongme': soluongme,
            'docs1': docs1,
            'docs2': docs2,
            'lenhsx': lenhsx,
            'khoiluong1mechaylai': khoiluong1mechaylai,
            'chaylai': chaylai,
            'parameters': parameters,
        }
