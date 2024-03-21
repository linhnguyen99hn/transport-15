# -*- coding: utf-8 -*-

from odoo import models, fields, api

from datetime import datetime, timedelta

from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT


class LenhtaohatWizard(models.TransientModel):
    _name = 'lenh.tao.hat.wizard'

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
    may = fields.Char('Máy')
    tocdocaplieu = fields.Float('Tốc độ cấp liệu')
    ghichu1 = fields.Char('Ghi chú')
    tocdotrucvit = fields.Float('Tốc độ trục vít')
    ghichu2 = fields.Char('Ghi chú')
    tocdogiaocat = fields.Float('Tốc độ giao cắt')
    ghichu3 = fields.Char('Ghi chú')
    noidungkiemtra = fields.Char('Nội dung kiểm tra')
    tieuchuansanpham = fields.Char('Tiêu chuẩn sản phẩm')
    ghichu = fields.Char('Ghi chú')
    bangnhietdo = fields.Many2one('nhiet.do', 'Bảng nhiệt độ tiêu chuẩn')
    soluongme = fields.Float('Số lượng mẻ')
    khoiluongmotme = fields.Float('Khối lượng 1 mẻ')

    dh1 = fields.Float('DH01')
    dh2 = fields.Float('DH02')
    dh3 = fields.Float('DH03')
    dh4 = fields.Float('DH04')
    dh5 = fields.Float('DH05')
    dh6 = fields.Float('DH06')
    dh7 = fields.Float('DH07')
    dh8 = fields.Float('DH08')
    dh9 = fields.Float('DH09')
    dh10 = fields.Float('DH010')
    dh11 = fields.Float('DH011')
    dh12 = fields.Float('DH012')
    dh13 = fields.Float('DH013')
    dh14 = fields.Float('DH014')

    def get_report(self):
        data = {
            'model': self._name,
            'ids': self.ids,
            'form': {
                'malenhsx': self.lenhsx.id, 'lenhsx': self.lenhsx.lenhsx, 'may': self.lenhsx.may_id.tenmay,
                'bangnhietdo': self.bangnhietdo.id,
                'tocdocaplieu': self.tocdocaplieu, 'tocdotrucvit': self.tocdotrucvit, 'tocdogiaocat': self.tocdogiaocat,
                'ghichu1': self.ghichu1, 'ghichu2': self.ghichu2, 'ghichu3': self.ghichu3,
                'soluongme': self.lenhsx.tongmesx, 'khoiluongmotme': self.lenhsx.khoiluongme,
                'dh1': self.bangnhietdo.dh1, 'dh2': self.bangnhietdo.dh2, 'dh3': self.bangnhietdo.dh3,
                'dh4': self.bangnhietdo.dh4, 'dh5': self.bangnhietdo.dh5,
                'dh6': self.bangnhietdo.dh6, 'dh7': self.bangnhietdo.dh7, 'dh8': self.bangnhietdo.dh8,
                'dh9': self.bangnhietdo.dh9, 'dh10': self.bangnhietdo.dh10,
                'dh11': self.bangnhietdo.dh11, 'dh12': self.bangnhietdo.dh12, 'dh13': self.bangnhietdo.dh13,
                'dh14': self.bangnhietdo.dh14,
            },
        }

        action = self.env.ref('mrp_fm.lenh_tao_hat').report_action(self, data=data)
        return action


class LenhSanXuat(models.AbstractModel):
    _name = 'report.mrp_fm.lenh_tao_hat_document'

    @api.model
    def _get_report_values(self, docids, data=None):
        lenhsx = data['form']['lenhsx']
        malenhsx = data['form']['malenhsx']
        may = data['form']['may']
        soluongme = data['form']['soluongme']
        khoiluongmotme = data['form']['khoiluongmotme']
        tocdocaplieu = data['form']['tocdocaplieu']
        tocdotrucvit = data['form']['tocdotrucvit']
        tocdogiaocat = data['form']['tocdogiaocat']
        ghichu1 = data['form']['ghichu1']
        ghichu2 = data['form']['ghichu2']
        ghichu3 = data['form']['ghichu3']
        dh1 = data['form']['dh1']
        dh2 = data['form']['dh2']
        dh3 = data['form']['dh3']
        dh4 = data['form']['dh4']
        dh5 = data['form']['dh5']
        dh6 = data['form']['dh6']
        dh7 = data['form']['dh7']
        dh8 = data['form']['dh8']
        dh9 = data['form']['dh9']
        dh10 = data['form']['dh10']
        dh11 = data['form']['dh11']
        dh12 = data['form']['dh12']
        dh13 = data['form']['dh13']
        dh14 = data['form']['dh14']

        bangnhietdo = data['form']['bangnhietdo']
        masx = self.env['kehoach.sanxuat'].search([('lenhsx_ids', '=', malenhsx)], limit=1).masx
        manoibo = self.env['cong.thuc.phoi.tron'].search([('id', '=', masx.id)]).tencongthuc
        # mi = self.env['cong.thuc.phoi.tron'].search([('id', '=', masx.id)]).mi

        param = {}
        param['lenhsx'] = malenhsx
        param['bangnhietdo'] = bangnhietdo
        query1 = """
                        SELECT tc.noidungkiemtra, tc.tieuchuansanpham, tc.ghichu
                        from lenh_san_xuat lsx
                               LEFT JOIN kehoach_sanxuat khsx ON khsx.lenhsx_ids = lsx.id
                               LEFT JOIN tieu_chuan_tao_hat tc ON tc.masx_ids=khsx.masx
                        where khsx.lenhsx_ids = %(lenhsx)s
                        group by tc.noidungkiemtra, tc.tieuchuansanpham, tc.ghichu
                        """
        self.env.cr.execute(query1, param)
        data_tieuchuan = self.env.cr.fetchall()
        _ids = []
        for line in data_tieuchuan:
            data_row = ({
                'noidungkiemtra': line[0],
                'tieuchuansanpham': line[1],
                'ghichu': line[2],
                'lenhsx': malenhsx,
            })
            _ids.append(self.env['lenh.tao.hat.wizard'].create(data_row).id)

        docs1 = self.env['lenh.tao.hat.wizard'].browse(_ids)

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
            'lenhsx': lenhsx,
            'manoibo': manoibo,
            'may': may,
            'khoiluongmotme': khoiluongmotme,
            'soluongme': soluongme,
            # 'mi': mi,
            'tocdocaplieu': tocdocaplieu,
            'tocdotrucvit': tocdotrucvit,
            'tocdogiaocat': tocdogiaocat,
            'ghichu1': ghichu1,
            'ghichu2': ghichu2,
            'ghichu3': ghichu3,
            'docs1': docs1,
            'dh1': dh1,
            'dh2': dh2,
            'dh3': dh3,
            'dh4': dh4,
            'dh5': dh5,
            'dh6': dh6,
            'dh7': dh7,
            'dh8': dh8,
            'dh9': dh9,
            'dh10': dh10,
            'dh11': dh11,
            'dh12': dh12,
            'dh13': dh13,
            'dh14': dh14,
            'parameters': parameters,
        }
