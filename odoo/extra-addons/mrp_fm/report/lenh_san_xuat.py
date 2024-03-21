# -*- coding: utf-8 -*-

from odoo import models, fields, api

from datetime import datetime, timedelta

from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT


class InlenhsxWizard(models.TransientModel):
    _name = 'lenh.sx.wizard'

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
    hopdong = fields.Char('Hợp đồng số')
    masx = fields.Many2one('cong.thuc.phoi.tron', 'Mã sản xuất')
    khoiluongdukien = fields.Float('Khối lượng (KG)')
    khoiluongnvl = fields.Float('Khối lượng (KG)')
    khoiluongnvl1me = fields.Float('Khối lượng (KG)')
    ghichu = fields.Char('Ghi chú')
    khoiluongmotme = fields.Float('Khối lượng 1 mẻ')
    soluongme = fields.Float('Số lượng mẻ')
    manguyenlieu = fields.Char('Mã nguyên liệu')
    nguyenlieu = fields.Many2one('nguyen.lieu', 'Nguyên liệu')
    khoiluong = fields.Float('Khối lượng')
    tenquycach = fields.Char('Tên quy cách')
    maquycach = fields.Text('Mô tả')
    nhua = fields.Boolean('Nhựa')
    sobaonguyen = fields.Integer('Số bao nguyên')
    nhomnl = fields.Char('Nhóm nguyên liệu')
    premix = fields.Char('Tên Premix')
    stt = fields.Integer('Số thứ tự')
    quytrinhdolieu = fields.Char('Quy trình đổ liệu')
    def get_report(self):
        data = {
            'model': self._name,
            'ids': self.ids,
            'form': {
                'malenhsx': self.lenhsx.id, 'lenhsx': self.lenhsx.lenhsx, 'khoiluong1me': self.lenhsx.khoiluongme,
                'haohut': self.lenhsx.haohut,
                'mamay': self.lenhsx.may_id.mamay, 'tongnguyenlieucap': self.lenhsx.tongnguyenlieucap,
                'tongklme': self.lenhsx.khoiluongme, 'soluongme': self.lenhsx.tongmesx,
                'chaylai': self.lenhsx.chaylai, 'thanhphamchaylai': self.lenhsx.thanhphamchaylai,
                'khoiluong1mechaylai': self.lenhsx.khoiluong1mechaylai, 'sohopdong': self.lenhsx.sohopdong,
                'bophannhap': self.lenhsx.bophannhap, 'bophanxuat': self.lenhsx.bophanxuat, 'lydoxuat': self.lenhsx.lydoxuat
            },
        }

        action = self.env.ref('mrp_fm.lenh_san_xuat').report_action(self, data=data)
        return action


class LenhSanXuat(models.AbstractModel):
    _name = 'report.mrp_fm.lenh_san_xuat_document'

    @api.model
    def _get_report_values(self, docids, data=None):
        lenhsx = data['form']['lenhsx']
        malenhsx = data['form']['malenhsx']
        tongnguyenlieucap = data['form']['tongnguyenlieucap']
        tongklme = data['form']['tongklme']
        haohut = data['form']['haohut']
        masx = self.env['kehoach.sanxuat'].search([('lenhsx_ids', '=', malenhsx)], limit=1).masx
        mathuongmai = self.env['kehoach.sanxuat'].search([('lenhsx_ids', '=', malenhsx)], limit=1).mathuongmaisp
        khoiluong1me = data['form']['khoiluong1me']
        manoibo = self.env['cong.thuc.phoi.tron'].search([('id', '=', masx.id)]).tencongthuc
        mamay = data['form']['mamay']
        soluongme = data['form']['soluongme']
        thanhphamchaylai = data['form']['thanhphamchaylai']
        khoiluong1mechaylai = data['form']['khoiluong1mechaylai']
        chaylai = data['form']['chaylai']
        sohopdong = data['form']['sohopdong']
        bophannhap = data['form']['bophannhap']
        bophanxuat = data['form']['bophanxuat']
        lydoxuat = data['form']['lydoxuat']
        thoigianbatdaudukien = self.env['kehoach.sanxuat'].search([('lenhsx_ids', '=', malenhsx)],
                                                                  limit=1).thoigian_batdau
        thoigianketthucdukien = self.env['kehoach.sanxuat'].search([('lenhsx_ids', '=', malenhsx)],
                                                                   limit=1).thoigian_ketthuc
        if thoigianbatdaudukien:
            thoigianbatdaudukien = thoigianbatdaudukien.strftime('%d/%m/%Y')
        if thoigianketthucdukien:
            thoigianketthucdukien = thoigianketthucdukien.strftime('%d/%m/%Y')

        param = {}
        param['lenhsx'] = malenhsx
        query1 = """
                        SELECT nl.manguyenlieu, ct.nguyenlieu , ct.khoiluong,  nl.nhua
                                , (ct.khoiluong/25) As sobaonguyen, nnlc.manhom, ctpt.premix, ct.sothutu, ct.quytrinhdolieu
                        from lenh_san_xuat lsx
                                LEFT JOIN kehoach_sanxuat khsx ON khsx.lenhsx_ids = lsx.id
                                LEFT JOIN cong_thuc ct ON ct.sanpham_ids = khsx.masx
                                LEFT JOIN nguyen_lieu nl on nl.id = ct.nguyenlieu 
                                LEFT JOIN nhom_nguyen_lieu nnl on nnl.id = nl.nhomnguyenlieu
        						LEFT JOIN nhom_nguyen_lieu nnlc on nnlc.id=nnl.nhomcha
        						LEFT JOIN cong_thuc_phoi_tron ctpt on ctpt.id = khsx.masx

                        where khsx.lenhsx_ids = %(lenhsx)s
                        group by ct.nguyenlieu,  nl.manguyenlieu, ct.khoiluong, ct.id, lsx.khoiluongme ,nl.id, 
                                nnlc.manhom, ctpt.premix, ct.sothutu
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
                'nhua': line[3],
                'sobaonguyen': line[4],
                'nhomnl': line[5],
                'premix': line[6],
                'stt': line[7],
                'quytrinhdolieu': line[8],
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

        # Lấy Danh Tính Người Ký
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
            'tentphtkh': settings.get_param('MrpFm.tentphtkh', default=''),
            'tentpsanxuat': settings.get_param('MrpFm.tentpsanxuat', default=''),
            'tengdcongnghe': settings.get_param('MrpFm.tengdcongnghe', default=''),
            'tengdsanxuat': settings.get_param('MrpFm.tengdsanxuat', default=''),
            'tentonggiamdoc': settings.get_param('MrpFm.tentonggiamdoc', default=''),
            'tennguoilap': settings.get_param('MrpFm.tennguoilap', default=''),
        }

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'haohut': haohut,
            'manoibo': manoibo,
            'khoiluong1me': khoiluong1me,
            'tongnguyenlieucap': tongnguyenlieucap,
            'tongklme': tongklme,
            'soluongme': soluongme,
            'thanhphamchaylai': thanhphamchaylai,
            'khoiluong1mechaylai': khoiluong1mechaylai,
            'chaylai': chaylai,
            'docs1': docs1,
            'docs2': docs2,
            'lenhsx': lenhsx,
            'mamay': mamay,
            'sohopdong': sohopdong,
            'thoigianbatdaudukien': thoigianbatdaudukien,
            'thoigianketthucdukien': thoigianketthucdukien,
            'mathuongmai': mathuongmai,
            'bophannhap': bophannhap,
            'bophanxuat': bophanxuat,
            'lydoxuat': lydoxuat,
            'parameters': parameters
        }
