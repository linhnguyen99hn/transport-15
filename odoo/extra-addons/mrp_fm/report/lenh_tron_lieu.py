# -*- coding: utf-8 -*-

from odoo import models, fields, api

from datetime import datetime, timedelta

from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT


class InlenhsxWizard(models.TransientModel):
    _name = 'lenh.tron.lieu.wizard'

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
    khoiluongdukien = fields.Float('Khối lượng (KG)')
    khoiluongnvl = fields.Float('Khối lượng (KG)')
    khoiluongnvl1me = fields.Float('Khối lượng (KG)')
    khoiluongmotme = fields.Float('Khối lượng 1 mẻ')
    nguyenlieu = fields.Many2one('nguyen.lieu', 'Nguyên liệu')
    manguyenlieu = fields.Char('Mã nguyên liệu')

    khoiluong = fields.Float('Khối lượng')
    premix = fields.Char('Tên Premix')
    stt = fields.Integer('Số thứ tự')
    quytrinhdolieu = fields.Char('Quy trình đổ liệu')
    nhomnl = fields.Char('Nhóm nguyên liệu')

    noidung = fields.Char('Nội dung kiểm tra')
    tieuchuanthietbi = fields.Char('Tiêu chuẩn thiết bị')
    ghichu = fields.Char('Ghi chú')

    def get_report(self):
        data = {
            'model': self._name,
            'ids': self.ids,
            'form': {
                'malenhsx': self.lenhsx.id, 'lenhsx': self.lenhsx.lenhsx, 'khoiluong1me': self.lenhsx.khoiluongme,
                'mamay': self.lenhsx.may_id.mamay, 'tongmesx': self.lenhsx.tongmesx, 'haohut': self.lenhsx.haohut,
                'tongnguyenlieucap': self.lenhsx.tongnguyenlieucap,
                'khoiluongmotme': self.lenhsx.khoiluongme,
                'chaylai': self.lenhsx.chaylai, 'thanhphamchaylai': self.lenhsx.thanhphamchaylai,
                'khoiluong1mechaylai': self.lenhsx.khoiluong1mechaylai

            },
        }

        action = self.env.ref('mrp_fm.lenh_tron_lieu').report_action(self, data=data)
        return action


class LenhSanXuat(models.AbstractModel):
    _name = 'report.mrp_fm.lenh_tron_lieu_document'

    @api.model
    def _get_report_values(self, docids, data=None):
        lenhsx = data['form']['lenhsx']
        malenhsx = data['form']['malenhsx']
        haohut = data['form']['haohut']
        masx = self.env['kehoach.sanxuat'].search([('lenhsx_ids', '=', malenhsx)], limit=1).masx
        khoiluong1me = data['form']['khoiluong1me']
        manoibo = self.env['cong.thuc.phoi.tron'].search([('id', '=', masx.id)]).tencongthuc
        mamay = data['form']['mamay']
        tongmesx = data['form']['tongmesx']
        tongnguyenlieucap = data['form']['tongnguyenlieucap']
        khoiluongmotme = data['form']['khoiluongmotme']
        thanhphamchaylai = data['form']['thanhphamchaylai']
        khoiluong1mechaylai = data['form']['khoiluong1mechaylai']
        chaylai = data['form']['chaylai']

        param = {}
        param['lenhsx'] = malenhsx
        query1 = """
                        SELECT nl.manguyenlieu ,ct.nguyenlieu, ct.khoiluong, sum(khsx.khoiluong_dukien) As khoiluongdukien
                               , ct.khoiluong/lsx.khoiluongme*sum(khsx.khoiluong_dukien) As khoiluongnguyenlieu
                               , ct.khoiluong As khoiluongnguyenlieu1me, nnlc.manhom, ctpt.premix, ct.sothutu, ct.quytrinhdolieu
                        from lenh_san_xuat lsx
                               LEFT JOIN kehoach_sanxuat khsx ON khsx.lenhsx_ids = lsx.id
                               LEFT JOIN cong_thuc ct ON ct.sanpham_ids=khsx.masx
                                left join nguyen_lieu nl on nl.id = ct.nguyenlieu 
                                LEFT JOIN nhom_nguyen_lieu nnl on nnl.id = nl.nhomnguyenlieu
        						LEFT JOIN nhom_nguyen_lieu nnlc on nnlc.id=nnl.nhomcha
        						LEFT JOIN cong_thuc_phoi_tron ctpt on ctpt.id = khsx.masx

                        where khsx.lenhsx_ids = %(lenhsx)s
                        group by  nl.manguyenlieu, ct.nguyenlieu, ct.khoiluong, ct.id, lsx.khoiluongme,nl.id
                                , nnlc.manhom, ctpt.premix, ct.sothutu
                        order by ct.id
                        """
        self.env.cr.execute(query1, param)
        data_dinhmuc = self.env.cr.fetchall()
        _ids = []
        for line in data_dinhmuc:
            data_row = ({
                'manguyenlieu': line[0],
                'nguyenlieu': line[1],
                'khoiluong': line[2],
                'khoiluongdukien': line[3],
                'khoiluongnvl': line[4],
                'khoiluongnvl1me': line[5],
                'nhomnl': line[6],
                'premix': line[7],
                'stt': line[8],
                'quytrinhdolieu': line[9],
                'lenhsx': malenhsx,
            })
            _ids.append(self.env['lenh.tron.lieu.wizard'].create(data_row).id)

        docs1 = self.env['lenh.tron.lieu.wizard'].browse(_ids)
        query2 = """
                              SELECT tc.noidung, tc.tieuchuanthietbi, tc.ghichu
                              from lenh_san_xuat lsx
                                     LEFT JOIN kehoach_sanxuat khsx ON khsx.lenhsx_ids = lsx.id
                                     LEFT JOIN tieu_chuan_thiet_bi tc ON tc.masx_ids=khsx.masx
                              where khsx.lenhsx_ids = %(lenhsx)s
                              group by tc.noidung, tc.tieuchuanthietbi, tc.ghichu
                              """
        self.env.cr.execute(query2, param)
        data_tieuchuan = self.env.cr.fetchall()
        _ids = []
        for line in data_tieuchuan:
            data_row = ({
                'noidung': line[0],
                'tieuchuanthietbi': line[1],
                'ghichu': line[2],
                'lenhsx': malenhsx,

            })
            _ids.append(self.env['lenh.tron.lieu.wizard'].create(data_row).id)

        docs2 = self.env['lenh.tron.lieu.wizard'].browse(_ids)

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
            'tennguoilap': settings.get_param('MrpFm.tennguoilap', default=''),
        }

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'manoibo': manoibo,
            'haohut': haohut,
            'khoiluong1me': khoiluong1me,
            'tongnguyenlieucap': tongnguyenlieucap,
            'khoiluongmotme': khoiluongmotme,
            'thanhphamchaylai': thanhphamchaylai,
            'khoiluong1mechaylai': khoiluong1mechaylai,
            'chaylai': chaylai,
            'docs1': docs1,
            'docs2': docs2,
            'lenhsx': lenhsx,
            'mamay': mamay,
            'tongmesx': tongmesx,
            'parameters': parameters,
        }
