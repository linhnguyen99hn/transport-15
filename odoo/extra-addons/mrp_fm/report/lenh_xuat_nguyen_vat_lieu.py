# -*- coding: utf-8 -*-

from odoo import models, fields, api

from datetime import datetime, timedelta

from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT


class LenhxuatnguyenvatlieuWizard(models.TransientModel):
    _name = 'lenh.xuat.nguyen.vat.lieu.wizard'

    # _rec_name = 'date_start'
    @api.depends('create_date')
    def name_get(self):
        result = []
        for record in self:
            name = record.create_date.strftime('%d-%m-%Y')
            result.append((record.id, name))
        return result

    # Header
    lenhsx = fields.Many2one('lenh.san.xuat', 'Lệnh sản xuất số', required=True)

    masx = fields.Many2one('cong.thuc.phoi.tron', 'Mã sản xuất')
    matemsp = fields.Many2one('lenh.san.xuat', 'Mã tem sản phẩm')
    tptheoycsx = fields.Many2one('lenh.san.xuat', 'TP theo YCSX')
    hopdongso = fields.Many2one('lenh.sx.wizard', 'Hợp đồng số')
    khoiluongmotme = fields.Float('Khối lượng 1 mẻ')
    soluongme = fields.Float('Số lượng mẻ')
    masx = fields.Char('Mã sản xuất')
    matemsp = fields.Char('Mã tem sản phẩm')
    tptheoycsx = fields.Integer('TP theo YCSX')
    hopdongso = fields.Char('Hợp đồng số')

    bophanxuat = fields.Char('Bộ phân xuất')
    bophannhap = fields.Char('Bộ phân nhập')
    lydoxuat = fields.Char('Lý do xuất')
    ngayxuatkehoach = fields.Date('Ngày cấp kế hoạch')
    ngayxuatthucte = fields.Date('Ngày cấp thực tế')


    # Nguyên liệu
    manguyenlieu = fields.Char('Mã nguyên liệu') # fields.Many2one('nguyen.lieu', 'Mã nguyên liệu')
    tennguyenlieu = fields.Char('Tên nguyên liệu') # fields.Many2one('nguyen.lieu', 'Tên nguyên liệu')
    donvitinh = fields.Char('Đơn vị tính') # fields.Many2one('don.vi.tinh', 'Đơn vị tính')
    khoiluong = fields.Float('Khối lượng')
    soluongkehoach = fields.Float('Số lượng kế hoạch')
    soluongthucte = fields.Float('Số lượng thực tế')
    caplan_1 = fields.Float('Cấp lần 1')
    caplan_2 = fields.Float('Cấp lần 2')
    nhua = fields.Boolean('Nhựa')
    sobaonguyen = fields.Integer('Số bao nguyên')

    # # Vật tư
    # vattu = fields.Many2one('nguyen.lieu', 'Vật tư')

    #Premix
    khoiluongnvl1me = fields.Float('Khối lượng (KG)')
    premix = fields.Char('Tên Premix')
    stt = fields.Integer('Số thứ tự')

    def get_report(self):
        data = {
            'model': self._name,
            'ids': self.ids,
            'form': {
                'malenhsx': self.lenhsx.id, 'lenhsx': self.lenhsx.lenhsx, 'khoiluong1me': self.lenhsx.khoiluongme,
                'matemsp': self.lenhsx.matemsp, 'tptheoycsx': self.lenhsx.tptheoycsx, 'haohut': self.lenhsx.haohut,
                'bophanxuat': self.lenhsx.bophanxuat, 'bophannhap': self.lenhsx.bophannhap, 'lydoxuat': self.lenhsx.lydoxuat,
                'ngayxuatkehoach': self.ngayxuatkehoach, 'ngayxuatthucte': self.ngayxuatthucte,
                'manguyenlieu': self.manguyenlieu, 'tennguyenlieu': self.tennguyenlieu,
                'donvitinh': self.donvitinh, 'soluongkehoach': self.soluongkehoach,
                'khoiluongmotme': self.lenhsx.khoiluongme, 'soluongme': self.lenhsx.tongmesx,
                'soluongthucte': self.soluongthucte, 'tongnguyenlieucap': self.lenhsx.tongnguyenlieucap,
                'caplan_1': self.caplan_1, 'caplan_2': self.caplan_2, 'tongmesx': self.lenhsx.tongmesx,
                'chaylai': self.lenhsx.chaylai, 'thanhphamchaylai': self.lenhsx.thanhphamchaylai,
                'khoiluong1mechaylai': self.lenhsx.khoiluong1mechaylai,'mamay': self.lenhsx.may_id.mamay,

            },
        }

        action = self.env.ref('mrp_fm.lenh_xuat_nguyen_vat_lieu').report_action(self, data=data)
        return action


class LenhSanXuat(models.AbstractModel):
    _name = 'report.mrp_fm.lenh_xuat_nguyen_vat_lieu_document'

    @api.model
    def _get_report_values(self, docids, data=None):
        lenhsx = data['form']['lenhsx']
        malenhsx = data['form']['malenhsx']
        haohut = data['form']['haohut']
        masx = self.env['kehoach.sanxuat'].search([('lenhsx_ids', '=', malenhsx)], limit=1).masx
        hopdongso = self.env['kehoach.sanxuat'].search([('lenhsx_ids', '=', malenhsx)], limit=1).donhang
        sohopdong = self.env['don.hang'].search([('id', '=', hopdongso.id)]).madonhang
        manoibo = self.env['cong.thuc.phoi.tron'].search([('id', '=', masx.id)]).tencongthuc
        matemsp = data['form']['matemsp']
        tongnguyenlieucap = data['form']['tongnguyenlieucap']
        tptheoycsx = data['form']['tptheoycsx']
        bophanxuat = data['form']['bophanxuat']
        bophannhap = data['form']['bophannhap']
        lydoxuat = data['form']['lydoxuat']
        ngayxuatkehoach = data['form']['ngayxuatkehoach']
        ngayxuatthucte = data['form']['ngayxuatthucte']
        khoiluongmotme = data['form']['khoiluongmotme']
        soluongme = data['form']['soluongme']
        manguyenlieu = data['form']['manguyenlieu']
        tennguyenlieu = data['form']['tennguyenlieu']
        donvitinh = data['form']['donvitinh']
        soluongkehoach = data['form']['soluongkehoach']
        soluongthucte = data['form']['soluongthucte']
        caplan_1 = data['form']['caplan_1']
        caplan_2 = data['form']['caplan_2']
        khoiluong1me = data['form']['khoiluong1me']
        tongmesx = data['form']['tongmesx']
        thanhphamchaylai = data['form']['thanhphamchaylai']
        khoiluong1mechaylai = data['form']['khoiluong1mechaylai']
        chaylai = data['form']['chaylai']
        mamay = data['form']['mamay']


        param = {}
        param['lenhsx'] = malenhsx

        query1 = """
                        SELECT nl.tennguyenlieu, nl.manguyenlieu, dvt.donvitinh, sum(khsx.khoiluong_dukien)
                               , ct.khoiluong/lsx.khoiluongme*sum(khsx.khoiluong_dukien) As soluongkehoach, ct.khoiluong, nl.nhua
                               ,FLOOR(ct.khoiluong / 25) As sobaonguyen 
                               , ct.khoiluong As khoiluongnguyenlieu1me, ctpt.premix, ct.sothutu
                        from lenh_san_xuat lsx
                               LEFT JOIN kehoach_sanxuat khsx ON khsx.lenhsx_ids = lsx.id
                               LEFT JOIN cong_thuc ct ON ct.sanpham_ids=khsx.masx
                               left join nguyen_lieu nl on nl.id = ct.nguyenlieu 
							   left join nhom_nguyen_lieu nnl on nnl.id = nl.nhomnguyenlieu
							   left join nhom_nguyen_lieu nnlc on nnlc.id=nnl.nhomcha
                               left join don_vi_tinh dvt on dvt.id = nl.donvitinh
                               LEFT JOIN cong_thuc_phoi_tron ctpt on ctpt.id = khsx.masx
                        where khsx.lenhsx_ids = %(lenhsx)s and nnlc.manhom = 'NGUYENLIEU'
                        group by nl.manguyenlieu, nl.tennguyenlieu, dvt.donvitinh, ct.id, nl.nhua, lsx.khoiluongme
                                    ,ctpt.premix, ct.sothutu
                        order by ct.id
                        """
        self.env.cr.execute(query1, param)
        data_nguyenlieu = self.env.cr.fetchall()
        _ids = []
        for line in data_nguyenlieu:
            data_row = ({
                'tennguyenlieu': line[0],
                'manguyenlieu': line[1],
                'donvitinh': line[2],
                'soluongkehoach': line[4],
                'khoiluong': line[5],
                'nhua': line[6],
                'sobaonguyen': line[7],
                'khoiluongnvl1me': line[8],
                'premix': line[9],
                'stt': line[10],
                'soluongthucte': soluongthucte,
                'caplan_1': caplan_1,
                'caplan_2': caplan_2,
                'lenhsx': malenhsx,
            })
            _ids.append(self.env['lenh.xuat.nguyen.vat.lieu.wizard'].create(data_row).id)

        docs1 = self.env['lenh.xuat.nguyen.vat.lieu.wizard'].browse(_ids)

        query2 = """
                        SELECT mavattu, tenvattu, dvt.donvitinh, soluongkehoach, nl.manguyenlieu
                        from lenh_cap_vat_tu lc
                            left join don_vi_tinh dvt on dvt.id = lc.donvitinh
                            left join nguyen_lieu nl on nl.id = lc.mavattu
                        where lc.lenhsx_id = %(lenhsx)s 
                        order by lc.id
                        """
        self.env.cr.execute(query2, param)
        data_vattu = self.env.cr.fetchall()
        _ids = []
        for line in data_vattu:
            data_row = ({
                'manguyenlieu': line[4],
                'tennguyenlieu': line[1],
                'donvitinh': line[2],
                'soluongkehoach': line[3],
                'soluongthucte': soluongthucte,
                'caplan_1': caplan_1,
                'caplan_2': caplan_2,
                'lenhsx': malenhsx,
            })
            _ids.append(self.env['lenh.xuat.nguyen.vat.lieu.wizard'].create(data_row).id)

        docs2 = self.env['lenh.xuat.nguyen.vat.lieu.wizard'].browse(_ids)

        query3 = """
                                SELECT nl.tennguyenlieu, dvt.donvitinh, sum(khsx.khoiluong_dukien)
                                       , ct.khoiluong/lsx.khoiluongme*sum(khsx.khoiluong_dukien) As soluongkehoach
                                      , ct.khoiluong As khoiluongnguyenlieu1me, ct.khoiluong, nl.nhua
                                      ,FLOOR(ct.khoiluong / 25) As sobaonguyen
                                      , nl.manguyenlieu, ct.id , ctpt.premix, ct.sothutu
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
                                      ,FLOOR(ct.khoiluong/ 25) As sobaonguyen 
                                      , nl.manguyenlieu, ct.id , ctpt.premix, ct.sothutu
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
                'donvitinh': line[1],
                'soluongkehoach': line[3],
                'khoiluongnvl1me': line[4],
                'khoiluong': line[5],
                'nhua': line[6],
                'sobaonguyen': line[7],
                'manguyenlieu': line[8],
                'premix': line[10],
                'stt': line[11],
                'lenhsx': malenhsx,
            })
            _ids.append(self.env['lenh.xuat.nguyen.vat.lieu.wizard'].create(data_row).id)

        docs3 = self.env['lenh.xuat.nguyen.vat.lieu.wizard'].browse(_ids)

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
            'tentpsanxuat': settings.get_param('MrpFm.tentpsanxuat', default=''),
            'tengdcongnghe': settings.get_param('MrpFm.tengdcongnghe', default=''),
            'tenketoan': settings.get_param('MrpFm.tenketoan', default=''),
            'tengdsanxuat': settings.get_param('MrpFm.tengdsanxuat', default=''),
            'tentonggiamdoc': settings.get_param('MrpFm.tentonggiamdoc', default=''),
            'tennguoilap': settings.get_param('MrpFm.tennguoilap', default=''),
        }

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'lenhsx': lenhsx,
            'masx': masx,
            'haohut': haohut,
            'manoibo': manoibo,
            'hopdongso': hopdongso,
            'sohopdong': sohopdong,
            'khoiluongmotme': khoiluongmotme,
            'soluongme': soluongme,
            'matemsp': matemsp,
            'tongnguyenlieucap': tongnguyenlieucap,
            'tptheoycsx': tptheoycsx,
            'bophanxuat': bophanxuat,
            'bophannhap': bophannhap,
            'lydoxuat': lydoxuat,
            'ngayxuatkehoach': ngayxuatkehoach,
            'ngayxuatthucte': ngayxuatthucte,
            'manguyenlieu': manguyenlieu,
            'tennguyenlieu': tennguyenlieu,
            'donvitinh': donvitinh,
            'soluongkehoach': soluongkehoach,
            'soluongthucte': soluongthucte,
            'caplan_1': caplan_1,
            'caplan_2': caplan_2,
            'khoiluongnvl1me': khoiluong1me,
            'tongmesx': tongmesx,
            'thanhphamchaylai': thanhphamchaylai,
            'khoiluong1mechaylai': khoiluong1mechaylai,
            'chaylai': chaylai,
            'mamay': mamay,
            'docs1': docs1,
            'docs2': docs2,
            'docs3': docs3,
            'parameters': parameters,
        }
