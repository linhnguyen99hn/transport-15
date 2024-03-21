from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class \
        CongThucPhoiTron(models.Model):
    _name = "cong.thuc.phoi.tron"
    _rec_name = 'tencongthuc'

    @api.model
    def _default_banggia(self):
        latest_banggia = self.env['bang.gia'].search([], order='create_date desc', limit=1)
        return latest_banggia

    tencongthuc = fields.Char('Code filler')
    tensanpham = fields.Char('Tên sản phẩm')
    ngaybatdau = fields.Date('Ngày bắt đầu')
    ngayketthuc = fields.Date('Ngày kết thúc')
    dinhmuc = fields.One2many('cong.thuc', 'sanpham_ids', 'Định mức phần trăm')
    banggia = fields.Many2one('bang.gia', 'Bảng giá', default=lambda self: self._default_banggia())
    premix = fields.Char('Tên Premix')

    dongia = fields.Float('Đơn giá', compute='tinh_don_gia', store=True)
    khoiluongme = fields.Float('Khối lượng 1 mẻ', compute='tinh_khoiluongme', store=True)
    chiphinhancong = fields.Float('Chi phí gia công', compute='tinh_chi_phi_nhan_cong', store=True)
    tongdongia = fields.Float('Tổng Đơn giá', compute='tinh_tong_don_gia')
    chiphivobao = fields.Float('Chi phí vỏ bao, túi lót')
    chiphibaozumbo = fields.Float('Chi phí bao zumbo')
    chiphiballetquanmang = fields.Float('Chi phí ballet quấn màng')

    # mi = fields.Char('MI')
    tieuchuansanpham = fields.One2many('tieu.chuan.tao.hat', 'masx_ids', 'Tiêu chuẩn sản phẩm')
    tieuchuanthietbi = fields.One2many('tieu.chuan.thiet.bi', 'masx_ids', 'Tiêu chuẩn thiết bị')
    dongianhancong_ids = fields.One2many('chi.phi.nhan.cong', 'congthuc_ids', 'Chi phí nhân công')

    @api.depends('dinhmuc.khoiluong')
    def tinh_khoiluongme(self):
        for rec in self:
            tongdinhmuc = sum(rec.dinhmuc.mapped('khoiluong'))
            rec.khoiluongme = tongdinhmuc

    @api.depends('dinhmuc.nguyenlieu', 'dinhmuc.khoiluong', 'banggia')
    def tinh_don_gia(self):
        self.dongia = 0.00
        banggia = self.env['gia.nguyen.lieu'].search([('bang_gia_ids', '=', self.banggia.id)])
        for record in self.dinhmuc:
            gianguyenlieu = next(filter(lambda r: r.nguyenlieu == record.nguyenlieu, banggia), False)
            if self.khoiluongme > 0:
                if gianguyenlieu:
                    if gianguyenlieu.dongia:
                        self.dongia += gianguyenlieu.dongia * (record.khoiluong / self.khoiluongme)
                    else:
                        raise ValidationError(
                            _("Nguyên liệu " + str(record.nguyenlieu.tennguyenlieu) + " chưa có đơn giá"))

    @api.depends('dongianhancong_ids.dongia', 'dongianhancong_ids.dongialuong')
    def tinh_chi_phi_nhan_cong(self):
        self.chiphinhancong = 0.00
        for record in self.dongianhancong_ids:
            if record.dongia:
                if record.dongia > 0:
                    self.chiphinhancong += record.dongia
                    # self.chiphinhancong += record.dongialuong.dongia * (record.khoiluong/self.khoiluongme)
                else:
                    raise ValidationError(_("Đơn giá nhân công " + str(record.dongialuong.ten) + " chưa có đơn giá"))

    @api.depends('dinhmuc.nguyenlieu', 'dinhmuc.khoiluong', 'banggia','chiphivobao','chiphibaozumbo','chiphiballetquanmang',
                 'dongianhancong_ids.dongia', 'dongianhancong_ids.dongialuong','dongia','chiphinhancong'
                 )
    def tinh_tong_don_gia(self):
        for rec in self:
            rec.tongdongia = 0.0
            rec.tongdongia = rec.dongia + rec.chiphinhancong + rec.chiphivobao + rec.chiphibaozumbo + rec.chiphiballetquanmang

    @api.onchange('dinhmuc')
    def onchange_stt(self):
        for rc in self.dinhmuc:
            if rc.sothutu_display == 0:
                rc.sothutu_display = len(self.dinhmuc)


class Congthuc(models.Model):
    _name = "cong.thuc"

    sanpham_ids = fields.Many2one('cong.thuc.phoi.tron', 'Công thức phối trộn')
    nguyenlieu = fields.Many2one('nguyen.lieu', 'Nguyên liệu')
    manguyenlieu = fields.Char(string='Mã nguyên liệu', related='nguyenlieu.manguyenlieu', store=True)
    khoiluong = fields.Float('Khối lượng')
    sothutu_display = fields.Integer('STT', default=1)
    quytrinhdolieu = fields.Char('Quy trình đổ liệu')
    sothutu = fields.Integer('STT', compute='_compute_sothutu_display', store=True)
    phantram = fields.Float('Phần trăm', compute='tinh_phan_tram', store=True)

    @api.depends('sanpham_ids.dinhmuc', 'sanpham_ids.dinhmuc.sothutu_display')
    def _compute_sothutu_display(self):
        for record in self:
            if record.sanpham_ids.dinhmuc:
                sequence = 1
                for line in record.sanpham_ids.dinhmuc.sorted(key=lambda r: r.sothutu_display):
                    if line == record:
                        record.sothutu = str(sequence)
                        break
                    sequence += 1
            else:
                record.sothutu = "1"

    @api.depends('nguyenlieu', 'khoiluong', 'sanpham_ids.khoiluongme')
    def tinh_phan_tram(self):
        for rec in self:
            if rec.sanpham_ids.khoiluongme > 0:
                rec.phantram = rec.khoiluong / rec.sanpham_ids.khoiluongme * 100


class Chiphinhancong(models.Model):
    _name = "chi.phi.nhan.cong"

    congthuc_ids = fields.Many2one('cong.thuc.phoi.tron', 'Công thức')
    dongialuong = fields.Many2one('don.gia.luong', 'Loại nhân công')
    dongia = fields.Float('Đơn giá')
