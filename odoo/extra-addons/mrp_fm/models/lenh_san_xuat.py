from odoo import _, api, fields, models, SUPERUSER_ID, tools
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta
from math import ceil, sqrt


class Lenhsanxuat(models.Model):
    _name = "lenh.san.xuat"
    _rec_name = 'lenhsx'

    lenhsx = fields.Char('Lệnh sản xuất', readonly='True')
    kehoach = fields.One2many('kehoach.sanxuat', 'lenhsx_ids', 'Kế hoạch chi tiết')

    tongnguyenlieucap = fields.Float('Tổng nguyên liệu cấp', compute='tinh_tong_nguyen_lieu', readonly=True, store=True)
    tongnguyenlieutheotp = fields.Float('Tổng nguyên liệu cấp theo thành phẩm', compute='tinh_tong_nguyen_lieu_tp', readonly=True, store=True)
    tongmesx = fields.Float('Tổng số mẻ SX', compute='_tinh_so_me', store=True)
    khoiluongme = fields.Float('Khối lượng 1 mẻ')
    matemsp = fields.Char('Mã tem sản phẩm')
    tptheoycsx = fields.Float('TP theo YCSX', compute='_tinh_khoiluong_theo_kehoach', store=True)
    bophanxuat = fields.Char('Bộ phân xuất')
    bophannhap = fields.Char('Bộ phận nhập')
    lydoxuat = fields.Char('Lý do xuất')
    ngaycapkehoach = fields.Date('Ngày cấp kế hoạch')
    ngaycapthucte = fields.Date('Ngày cấp thực tế')

    sohopdong = fields.Char('Số hợp đồng', compute='_lay_thong_tin_so_hop_dong', store=True)
    may_id = fields.Many2one('dm.may', 'Máy chạy', compute='_lay_thong_tin_may', store=True)
    haohut = fields.Float('Hao hụt', compute='tinh_hao_hut', store=True)
    # thanhphamnhanduoc = fields.Float('Thành phẩm nhận được', compute='tinh_tong_nguyen_lieu', store=True)

    lenhcapvattu_ids = fields.One2many('lenh.cap.vat.tu', 'lenhsx_id', 'Vật tư chi tiết')
    lenhcapnlpremix = fields.One2many('lenh.cap.premix', 'lenhsx_id', 'Vật tư chi tiết')

    chaylai = fields.Boolean('Có thành phẩm chạy lại', default=False)
    thanhphamchaylai = fields.Char('Thành phẩm chạy lại')
    khoiluong1mechaylai = fields.Float('Khối lượng thành phẩm chạy lại')
    thanhphamnhanduoc = fields.Float('Hao hụt', compute='tinh_thanh_pham_nhan_duoc', store=True)

    @api.model
    def create(self, vals_list):
        data = super(Lenhsanxuat, self).create(vals_list)
        seq = self.env.ref('mrp_fm.sequence_ma_lenh_san_xuat')
        data.lenhsx = seq.next_by_id()
        return data

    @api.depends('kehoach', 'kehoach.khoiluong_dukien')
    def _tinh_khoiluong_theo_kehoach(self):
        for rec in self:
            if len(rec.kehoach) > 0:
                kltheokehoach = sum(rec.kehoach.mapped('khoiluong_dukien'))
                rec.tptheoycsx = kltheokehoach
            else:
                rec.tptheoycsx = 0

    @api.depends('kehoach', 'kehoach.kh_may_id')
    def _lay_thong_tin_may(self):
        for rec in self:
            if len(rec.kehoach) > 0:
                rec.may_id = rec.kehoach[0].kh_may_id

    @api.depends('kehoach', 'kehoach.madonhang')
    def _lay_thong_tin_so_hop_dong(self):
        for rec in self:
            if len(rec.kehoach) > 0:
                rec.sohopdong = rec.kehoach[0].madonhang
    @api.depends('tptheoycsx', 'kehoach', 'kehoach.khoiluong_dukien')
    def tinh_hao_hut(self):
        for rec in self:
            if rec.may_id.mamay == "4":
                haohut = 0.7
                rec.haohut = haohut
            else:
                if rec.tptheoycsx <= 25000:
                    haohut = 0.8
                    rec.haohut = haohut
                elif 25000 < rec.tptheoycsx <= 100000:
                    haohut = 0.65
                    rec.haohut = haohut
                elif rec.tptheoycsx > 100000:
                    haohut = 0.5
                    rec.haohut = haohut

    @api.depends('tptheoycsx', 'haohut')
    def tinh_tong_nguyen_lieu_tp(self):
        for rec in self:
            tongnguyenlieu = rec.tptheoycsx * (1 + rec.haohut/100)
            rec.tongnguyenlieutheotp = tongnguyenlieu

    @api.depends('tongnguyenlieutheotp', 'khoiluongme')
    def _tinh_so_me(self):
        for rec in self:
            if rec.khoiluongme > 0:
                rec.tongmesx = ceil(rec.tongnguyenlieutheotp/rec.khoiluongme)

    @api.depends('tongnguyenlieutheotp', 'tongmesx')
    def tinh_tong_nguyen_lieu(self):
        for rec in self:
            rec.tongnguyenlieucap = rec.tongmesx * rec.khoiluongme

    @api.depends('tongnguyenlieucap', 'khoiluong1mechaylai', 'tongmesx', 'haohut', 'chaylai')
    def tinh_thanh_pham_nhan_duoc(self):
        for rec in self:
            if rec.chaylai == False:
                rec.thanhphamnhanduoc = rec.tongnguyenlieucap / (1 + rec.haohut/100)
            if rec.chaylai == True:
                rec.thanhphamnhanduoc = (rec.tongnguyenlieucap + rec.khoiluong1mechaylai) / (1 + rec.haohut/100)
class Lenhcapvattu(models.Model):
    _name = "lenh.cap.vat.tu"
    _rec_name = 'lenhsx_id'

    lenhsx_id = fields.Many2one('lenh.san.xuat', 'Lệnh sản xuất')

    mavattu = fields.Many2one('nguyen.lieu', 'Mã vật tư', domain="[('nhomnguyenlieu', '=', 'sản phẩm')]")
    tenvattu = fields.Char(related='mavattu.tennguyenlieu', string='Tên vật tư', store=True)
    donvitinh = fields.Many2one('don.vi.tinh', related='mavattu.donvitinh', string='Đơn vị tính', store=True)
    soluongkehoach = fields.Float('Số lượng kế hoạch', compute='tinh_so_luong_theo_dinh_muc', store=True, readonly=False)

    @api.depends('mavattu', 'lenhsx_id', 'lenhsx_id.tptheoycsx', 'lenhsx_id.kehoach')
    def tinh_so_luong_theo_dinh_muc(self):
        for rec in self:
            if len(rec.lenhsx_id.kehoach) > 0:
                sanpham = rec.lenhsx_id.kehoach[0].sanpham
                trongluongbao = sanpham.trongluong
                trongluongpallet = sanpham.trongluongpallet
                if rec.mavattu.manguyenlieu:
                    if rec.donvitinh.donvitinh == 'Cái' and rec.mavattu.manguyenlieu[0:2] in ('VB', 'TL', 'TE') and trongluongbao > 0:
                        sobao = ceil(rec.lenhsx_id.tongnguyenlieucap / trongluongbao)
                        rec.soluongkehoach = sobao
                    if rec.donvitinh.donvitinh == 'Cái' and rec.mavattu.manguyenlieu[0:2] == 'PL' and trongluongpallet > 0:
                        sopallet = ceil(rec.lenhsx_id.tongnguyenlieucap / trongluongpallet)
                        rec.soluongkehoach = sopallet
                    if rec.donvitinh.donvitinh == 'Kg' and rec.mavattu.manguyenlieu[0:2] == 'TL' and trongluongbao > 0:
                        sobao = ceil(rec.lenhsx_id.tongnguyenlieucap / trongluongbao)
                        # IF(D68="Túi lót 24 gam (Túi lót nội địa)";K67*24,5/1000;
                        # IF(D68="túi lót 18 gam (Túi lót xuất khẩu)";K67*18,5/1000;
                        # IF(D68="Túi lót 25 gam (Túi lót dài)";K67*25,5/1000;
                        # IF(D68="Túi lót bao jumbo 90x90x125cm";K67*550/1000)))))
                        # ----- TL1, TL2, TL5, TL6, TL7
                        if rec.mavattu.manguyenlieu == 'TL1':
                            rec.soluongkehoach = sobao * 24.5 / 1000
                        if rec.mavattu.manguyenlieu == 'TL2':
                            rec.soluongkehoach = sobao * 25.5 / 1000
                        if rec.mavattu.manguyenlieu == 'TL5':
                            rec.soluongkehoach = sobao * 18.5 / 1000

class Lenhcapnlpremix(models.Model):
    _name = "lenh.cap.premix"
    _rec_name = 'lenhsx_id'

    lenhsx_id = fields.Many2one('lenh.san.xuat', 'Lệnh sản xuất')
    manguyenlieu = fields.Many2one('nguyen.lieu', 'Mã nguyên liệu',)
    tennguyenlieu = fields.Char(related='manguyenlieu.tennguyenlieu', string='Tên nguyên liệu', store=True)
    tile = fields.Float('Tỉ lệ %')
    khoiluonglo = fields.Float('Khối lượng(kg)/Lô sx')
    khoiluongme = fields.Float('Khối lượng(kg)/Mẻ')
    khoiluongcan = fields.Float('Khối lượng cân(kg')
    khoiluongcancobi = fields.Float('Khối lượng cân có bì(kg)')
