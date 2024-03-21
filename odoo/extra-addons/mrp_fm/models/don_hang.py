from odoo import _, api, fields, models, SUPERUSER_ID, tools
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta, time


class DonHang(models.Model):
    _name = "don.hang"
    _rec_name = 'madonhang'
    _order = 'ngaydat DESC'

    madonhang = fields.Char('Số hợp đồng')
    makhach = fields.Many2one('dm.khach', 'Khách hàng')
    ngaydat = fields.Date('Ngày đặt')
    # phuongthucthanhtoan = fields.Char('Phương thức thanh toán')
    # thoihanthanhtoan = fields.Date('Thời hạn thanh toán')
    # diadiemgiao = fields.Char('Địa điểm giao hàng')
    mucdouutien = fields.Selection([('1.uutien', 'Ưu tiên'), ('2.dukien', 'Dự kiến'), ('3.sanxuat', 'Sản xuất')],
                                   'Mức độ ưu tiên', required=True)
    canhbao = fields.Boolean('Cảnh báo', default=False, compute='donhang_canhbao_giaohang', store=True)
    canhbao_badge_donhang = fields.Html(string="Cảnh báo Badge", compute='_compute_canhbao_badge', store=True)
    donhangchitiet_ids = fields.One2many('donhang.chitiet', 'donhang_id', 'Đơn hàng chi tiết')
    banggia = fields.Many2one('bang.gia', 'Bảng giá', required=True)
    trangthaidonhang = fields.Selection(
        [('chosx', 'Chờ sản xuất'), ('sanxuat', 'Đang sản xuất'), ('hoanthanh', 'Hoàn thành')],
        'Trang thái', compute='compute_trang_thai_don_hang', store=True)

    @api.depends('canhbao')
    def _compute_canhbao_badge(self):
        for record in self:
            if record.canhbao:
                record.canhbao_badge_donhang = '<span class="badge badge-pill badge-danger">Chậm Tiến Độ</span>'
            else:
                record.canhbao_badge_donhang = ''

    @api.depends('donhangchitiet_ids.kehoach_ids', 'donhangchitiet_ids.kehoach_ids.chenhlech',
                 'donhangchitiet_ids.kehoach_ids.thoigian_ketthuc', 'donhangchitiet_ids.ngaygiao',
                 'donhangchitiet_ids.canhbao')
    def donhang_canhbao_giaohang(self):
        for rec in self:
            if len(rec.donhangchitiet_ids) > 0:
                # for chitiet in rec.donhangchitiet_ids:
                #     sodonchitietcocanhbao = sum(1 for chitiet in rec.donhangchitiet_ids if chitiet.canhbao == 'True')

                sodonchitietcocanhbao = len(rec.donhangchitiet_ids.filtered(lambda chitiet: chitiet.canhbao == 'True'))
                if sodonchitietcocanhbao > 0:
                    rec.canhbao = True
                else:
                    rec.canhbao = False
            else:
                rec.canhbao = False

    @api.depends('donhangchitiet_ids.trangthai')
    def compute_trang_thai_don_hang(self):
        for rec in self:
            if len(rec.donhangchitiet_ids) > 0:
                for chitiet in rec.donhangchitiet_ids:
                    sodonchitietchosx = sum(1 for chitiet in rec.donhangchitiet_ids if chitiet.trangthai == 'chosx')
                    sodonchitietsanxuat = sum(1 for chitiet in rec.donhangchitiet_ids if chitiet.trangthai == 'sanxuat')
                    sodonchitiethoanthanh = sum(
                        1 for chitiet in rec.donhangchitiet_ids if chitiet.trangthai == 'hoanthanh')

                if sodonchitietsanxuat > 0:
                    rec.trangthaidonhang = 'sanxuat'
                elif sodonchitietchosx > 0 and sodonchitiethoanthanh > 0:
                    rec.trangthaidonhang = 'sanxuat'
                elif sodonchitietchosx > 0 and sodonchitiethoanthanh == 0 and sodonchitietsanxuat == 0:
                    rec.trangthaidonhang = 'chosx'
                elif sodonchitietchosx == 0 and sodonchitiethoanthanh > 0 and sodonchitietsanxuat == 0:
                    rec.trangthaidonhang = 'hoanthanh'


class DonhangChitiet(models.Model):
    _name = 'donhang.chitiet'
    _rec_name = 'mathuongmaisp'

    mathuongmaisp = fields.Many2one('dm.sanpham', 'Mã thương mại')
    ngaydat = fields.Date('Ngày đặt')
    ngaygiao = fields.Datetime('Ngày đóng hàng', required=True)
    soluong = fields.Float('Số lượng')
    tensanpham = fields.Char('Tên sản phẩm', compute='_compute_tensanpham', store=True)

    donhang_id = fields.Many2one('don.hang', 'Đơn hàng')
    kehoach_ids = fields.One2many('kehoach.sanxuat', 'donhangchitiet_id', 'Kế hoạch chi tiết')

    tinhtrangkehoach = fields.Selection([('chuaco', 'Chưa có kế hoạch'), ('daco', 'Đã có kế hoạch')],
                                        'Tình trạng kế hoạch', compute='_tinh_tinhtrang_kehoach', store=True)
    soluongdacokehoach = fields.Float('Số lượng đã lập kế hoạch', compute='_tinh_soluong_daco_kehoach', default=0,
                                      store=True)
    soluongchuacokehoach = fields.Float('Số lượng cần lập kế hoạch', compute='_tinh_soluong_chuaco_kehoach', store=True)

    dasanxuat = fields.Float('Dữ liệu tạm', default=0)
    tonkhobotri = fields.Float('Số lượng sử dụng từ tồn kho', default=0)
    canhbao = fields.Boolean('Cảnh báo', default=False, compute='canhbao_giaohang', store=True)
    canhbao_badges = fields.Html(string="Cảnh báo Badge", compute='_compute_canhbao_badges', store=True)
    masx = fields.Many2one('cong.thuc.phoi.tron', 'Mã sản xuất', compute='tinh_manoibo', store=True)
    chamgiaohang = fields.Char('Thời gian chậm giao hàng', default="", compute='canhbao_giaohang', store=True)
    trangthai = fields.Selection([('chosx', 'Chờ sản xuất'), ('sanxuat', 'Đang sản xuất'), ('hoanthanh', 'Hoàn thành')],
                                 'Trang thái', compute='compute_trang_thai', store=True)

    @api.depends('mathuongmaisp')
    def tinh_manoibo(self):
        for rec in self:
            if rec.mathuongmaisp:
                rec.masx = rec.mathuongmaisp.manoibosp

    @api.depends('kehoach_ids')
    def _tinh_tinhtrang_kehoach(self):
        for rec in self:
            if len(rec.kehoach_ids) > 0:
                rec.tinhtrangkehoach = 'daco'
            else:
                rec.tinhtrangkehoach = 'chuaco'

    @api.depends('kehoach_ids', 'kehoach_ids.khoiluong_dukien')
    def _tinh_soluong_daco_kehoach(self):
        for rec in self:
            if len(rec.kehoach_ids) > 0:
                soluongdacokehoach = sum(rec.kehoach_ids.mapped('khoiluong_dukien'))
                rec.soluongdacokehoach = soluongdacokehoach
            else:
                rec.soluongdacokehoach = 0

    @api.depends('soluong', 'soluongdacokehoach', 'tonkhobotri')
    def _tinh_soluong_chuaco_kehoach(self):
        for rec in self:
            rec.soluongchuacokehoach = rec.soluong - rec.tonkhobotri - rec.soluongdacokehoach

    @api.depends('mathuongmaisp')
    def _compute_tensanpham(self):
        for rec in self:
            rec.tensanpham = rec.mathuongmaisp.tensanpham

    def action_lap_ke_hoach(self):
        lkh_obj = self.env['lkh'].create({})
        return lkh_obj.lapkehoachsanxuat(self)

    def btn_xemkehoachdet(self):
        kehoachsx_ids = self.env['kehoach.sanxuat'].search([])
        ke_hoach_view_id = self.env.ref('mrp_fm.kehoachsanxuat_timeline_view').id
        return {
            'name': 'Bảng phân bổ kế hoạch',
            'type': 'ir.actions.act_window',
            'res_model': 'kehoach.sanxuat',
            'view_mode': 'timeline',
            'view_id': ke_hoach_view_id,
            # 'res_id': self.id,
            # 'target': 'new',
            'domain': [('donhangchitiet_id', '=', self.id)],
            'context': {
                'lenhsx_ids': kehoachsx_ids,
            }
        }

    @api.depends('kehoach_ids', 'kehoach_ids.chenhlech', 'kehoach_ids.thoigian_ketthuc', 'ngaygiao')
    def canhbao_giaohang(self):
        for rec in self:
            tongchenhlech = sum(rec.kehoach_ids.mapped('chenhlech'))
            if tongchenhlech < 0:
                rec.canhbao = True
                chenhlech = abs(tongchenhlech)
                kehoachhientai = self.env['kehoach.sanxuat'].search([('donhangchitiet_id', '=', rec.id)],
                                                                    order='thoigian_ketthuc DESC')
                # may_id = kehoachhientai[0]['kh_may_id'].mamay
                # csmay_id = self.env['congsuat.may'].search([('may_ids.mamay', '=', may_id), (
                #                 'sanpham_ids.mathuongmaisp', '=', rec.mathuongmaisp.mathuongmaisp)])
                # csmay = csmay_id['congsuat']
                congsuat = kehoachhientai[0].congsuat
                if congsuat > 0:
                    chamgiaogio = '{:.2f}'.format(chenhlech / congsuat)
                    # chamgiaophut = int((chenhlech - chamgiaogio) * 60)
                    ngay_gio_cham_giao = f"{(chamgiaogio)} giờ"
                    rec.chamgiaohang = ngay_gio_cham_giao
            else:
                rec.canhbao = False

            # kehoachhientai = self.env['kehoach.sanxuat'].search([('donhangchitiet_id', '=', rec.id)],
            #                                                     order='thoigian_ketthuc DESC')
            # if len(kehoachhientai) > 0:
            #     if kehoachhientai[0]['thoigian_ketthuc']:
            #         thoigianketthuccuoi = kehoachhientai[0]['thoigian_ketthuc']
            #         may_id = kehoachhientai[0]['kh_may_id'].mamay
            #         csmay_id = self.env['congsuat.may'].search([('may_ids.mamay', '=', may_id), (
            #             'sanpham_ids.mathuongmaisp', '=', rec.mathuongmaisp.mathuongmaisp)])
            #         csmay = csmay_id['congsuat']
            #         if csmay > 0:
            #             gio = int(tongchenhlech / csmay)
            #             phut = int(((tongchenhlech / csmay) - gio) * 60)
            #             thoigianchenhlech = timedelta(hours=gio, minutes=phut)
            #             # bugio = timedelta(hours=7, minutes=0)
            #             thoigianketthucmoi = (thoigianketthuccuoi + thoigianchenhlech) #- bugio
            #             if thoigianketthucmoi >= rec.ngaygiao:
            #                 rec.write({'canhbao': True})
            #                 chamgiaohang = thoigianketthucmoi - rec.ngaygiao
            #                 if chamgiaohang.days == 0:
            #                     ngay_gio_cham_giao = f"{int(chamgiaohang.seconds / 3600)} giờ"
            #                 else:
            #                     ngay_gio_cham_giao = f"{(chamgiaohang.days)} ngày {int(chamgiaohang.seconds/3600)} giờ"
            #                 rec.chamgiaohang = ngay_gio_cham_giao
            #             else:
            #                 rec.write({'canhbao': False})
            #                 rec.chamgiaohang = ""

    @api.depends('tinhtrangkehoach', 'kehoach_ids.khoiluong_dukien', 'kehoach_ids.khoiluong_thucte')
    def compute_trang_thai(self):
        for rec in self:
            if rec.tinhtrangkehoach == 'chuaco':
                rec.trangthai = 'chosx'
            else:
                tongkhoiluongdasx = sum(rec.kehoach_ids.mapped('khoiluong_thucte'))
                if tongkhoiluongdasx >= rec.soluong:
                    rec.trangthai = 'hoanthanh'
                else:
                    rec.trangthai = 'sanxuat'

    @api.depends('canhbao')
    def _compute_canhbao_badges(self):
        for record in self:
            if record.canhbao:
                # Sử dụng f-string để định dạng giá trị chamgiaohang dưới dạng giờ, phút, giây
                record.canhbao_badges = f'<span class="badge badge-pill badge-danger">Chậm {record.chamgiaohang}</span>'
            else:
                record.canhbao_badges = ''


class KehoachSanxuat(models.Model):
    _name = 'kehoach.sanxuat'
    _rec_name = 'lenhsx_ids'

    def name_get(self):
        result = []
        for rec in self:
            name = f"{rec.donhang.madonhang}/{rec.sanpham.mathuongmaisp}".upper() if rec.donhang and rec.sanpham else ''
            result.append((rec.id, name))
        return result

    lenhsx_ids = fields.Many2one('lenh.san.xuat', 'Lệnh sản xuất')
    donhang = fields.Many2one('don.hang', 'Đơn hàng')
    donhangchitiet_id = fields.Many2one('donhang.chitiet', 'Sản phẩm', domain="[('donhang_id', '=?', donhang)]")
    sanpham = fields.Many2one('dm.sanpham', 'Sản phẩm', compute='_compute_sanpham', store=True)
    masx = fields.Many2one('cong.thuc.phoi.tron', 'Mã sản xuất', compute='tinh_masx', store=True)

    madonhang = fields.Char(related='donhang.madonhang')  # 'Số hợp đồng')
    mathuongmaisp = fields.Char(related='sanpham.mathuongmaisp')  # 'Mã thương mại')
    manoibosp = fields.Char(related='sanpham.manoibosp.tencongthuc')  # 'Code filler')

    kh_may_id = fields.Many2one('dm.may', 'Máy chạy')
    ngay = fields.Date('Ngày', compute='_tinh_ngay_kehoach', store=True)
    sophieunhap = fields.Char('Số phiếu nhập')
    quyenso = fields.Char('Quyển số')

    khoiluong_dukien = fields.Float('Khối lượng dự kiến', required=True)
    khoiluong_thucte = fields.Float('Khối lượng thực tế')
    chenhlech = fields.Float('Chênh lệch', compute='_tinh_chenh_lech', store=True, readonly='True')
    phe = fields.Float('Phế')
    ban_thanh_pham = fields.Float('Bán thành phẩm')
    hao_phi = fields.Float('Khối lượng hao phí', )  # compute='tinh_hao_phi', store=True

    thoigian_batdau = fields.Datetime('Thời gian bắt đầu')
    thoigian_ketthuc = fields.Datetime('Thời gian kết thúc', compute='_tinh_thoigian_ketthuc', store=True)
    thoigian_dukien = fields.Float('Thời gian dự kiến (giờ)', compute='tinh_thoi_gian_du_kien', store=True)

    thoigian_chuyendoi = fields.Float('Thời gian chuyển đổi (giờ)')
    thoigian_batdau_thucte = fields.Datetime('Thời gian bắt đầu')
    thoigian_ketthuc_thucte = fields.Datetime('Thời gian kết thúc', )
    thoigian_dungnghihetca = fields.Float('Thời gian dừng nghỉ hết ca(phút)')
    thoigian_dungtheokh = fields.Float('Thời gian dừng theo kế hoạch(phút)')
    thoigian_dungsucokhac = fields.Float('Thời gian dừng sự cố khác(phút)')
    thoigian_dungkithuat = fields.Float('Thời gian dừng kĩ thuật(phút)')
    thoigian_chaymay_thucte = fields.Float('Thời gian chạy máy thực tế', compute='tinh_thoi_gian_thuc_te', store=True)
    thoigian_haophi = fields.Float('Thời gian hao phí(phút)', compute='tinh_thoi_gian_hao_phi', store=True)

    mucdouutien = fields.Selection([('1.uutien', 'Ưu tiên'), ('2.dukien', 'Dự kiến'), ('3.sanxuat', 'Sản xuất')],
                                   'Mức độ ưu tiên', compute='_tinh_mucdo_uutien', store=True)
    congsuat = fields.Float('Công suất', compute='tinh_cong_suat', store=True)
    phantramhoanthanh = fields.Float('% hoàn thành', compute='tinh_phan_tram_hoan_thanh', store=True)
    nangsuatbinhquan = fields.Float('Năng suất bình quân', compute='tinh_nang_suat_binh_quan', store=True)
    ghichu = fields.Char('Nguyên nhân')
    chamgiaohang = fields.Char('Thời gian chậm giao hàng', default="", compute='canhbao_chenhlech', store=True)
    canhbao = fields.Boolean('Cảnh báo', default=False, compute='canhbao_chenhlech', store=True)
    canhbao_badges_chenhlech = fields.Html(string="Cảnh báo Badge", compute='_compute_canhbao_badges_chenhlech',
                                           store=True)
    canhbao_badges_chenhlechs = fields.Html(string="Cảnh báo Badge", compute='_compute_canhbao_badges_chenhlech',
                                            store=True)

    # Cảnh Báo Chênh Lệch
    @api.depends('chenhlech', 'congsuat')
    def canhbao_chenhlech(self):
        for rec in self:
            if rec.chenhlech < 0:
                if rec.congsuat > 0:
                    gio_du_kien = abs(rec.chenhlech) / rec.congsuat
                else:
                    gio_du_kien = 0.0
                rec.canhbao = True
                chamgiaogio = '{:.2f}'.format(gio_du_kien)
                ngay_gio_cham_giao = f"{(chamgiaogio)} giờ"
                rec.chamgiaohang = ngay_gio_cham_giao
            else:
                rec.canhbao = False

    @api.depends('canhbao')
    def _compute_canhbao_badges_chenhlech(self):
        for record in self:
            if record.canhbao:
                # Sử dụng f-string để định dạng giá trị chamgiaohang dưới dạng giờ, phút, giây
                record.canhbao_badges_chenhlechs = f'<span class="badge badge-pill badge-info">Chậm {record.chamgiaohang}</span>'
                record.canhbao_badges_chenhlech = f'<span class="badge badge-pill badge-danger">Chậm {record.chamgiaohang}</span>'
            else:
                record.canhbao_badges_chenhlechs = ''
                record.canhbao_badges_chenhlech = ''

    @api.depends('donhang')
    def _tinh_mucdo_uutien(self):
        for rec in self:
            if rec.donhang:
                rec.mucdouutien = rec.donhang.mucdouutien

    @api.depends('sanpham')
    def tinh_masx(self):
        for rec in self:
            if rec.sanpham:
                rec.masx = rec.sanpham.manoibosp

    @api.depends('donhangchitiet_id')
    def _compute_sanpham(self):
        for rec in self:
            if rec.donhangchitiet_id:
                rec.sanpham = rec.donhangchitiet_id.mathuongmaisp.id

    @api.depends('khoiluong_dukien', 'khoiluong_thucte')
    def _tinh_chenh_lech(self):
        for rec in self:
            if rec.khoiluong_thucte:
                rec.chenhlech = rec.khoiluong_thucte - rec.khoiluong_dukien

    @api.depends('thoigian_batdau', 'thoigian_dukien')
    def _tinh_thoigian_ketthuc(self):
        for rec in self:
            if rec.thoigian_batdau and rec.thoigian_dukien:
                rec.thoigian_ketthuc = rec.thoigian_batdau + timedelta(hours=rec.thoigian_dukien)

    @api.depends('thoigian_batdau')
    def _tinh_ngay_kehoach(self):
        for rec in self:
            if rec.thoigian_batdau:
                rec.ngay = rec.thoigian_batdau.date()

    @api.depends('thoigian_batdau_thucte', 'thoigian_ketthuc_thucte', 'thoigian_haophi')
    def tinh_thoi_gian_thuc_te(self):
        for rec in self:
            if rec.thoigian_batdau_thucte and rec.thoigian_ketthuc_thucte:
                thoigian_batdau = fields.Datetime.from_string(rec.thoigian_batdau_thucte)
                thoigian_ketthuc = fields.Datetime.from_string(rec.thoigian_ketthuc_thucte)
                thoigian_chaymay = ((thoigian_ketthuc - thoigian_batdau).total_seconds()) / 3600
                rec.thoigian_chaymay_thucte = thoigian_chaymay - rec.thoigian_haophi / 60

    @api.depends('thoigian_dungnghihetca', 'thoigian_dungkithuat', 'thoigian_dungsucokhac', 'thoigian_dungtheokh')
    def tinh_thoi_gian_hao_phi(self):
        for rec in self:
            rec.thoigian_haophi = rec.thoigian_dungnghihetca + rec.thoigian_dungkithuat + rec.thoigian_dungsucokhac + \
                                  rec.thoigian_dungtheokh

    # @api.depends('khoiluong_dukien', 'khoiluong_thucte', 'phe', 'ban_thanh_pham')
    # def tinh_hao_phi(self):
    #     for r in self:
    #         r.hao_phi = r.khoiluong_dukien - r.khoiluong_thucte - r.phe - r.ban_thanh_pham

    @api.depends('sanpham', 'kh_may_id')
    def tinh_cong_suat(self):
        for rec in self:
            csmay = self.env['congsuat.may'].search([('may_ids.mamay', '=', rec.kh_may_id.mamay), (
                'sanpham_ids.mathuongmaisp', '=', rec.sanpham.mathuongmaisp)]).congsuat
            rec.congsuat = csmay

    @api.depends('khoiluong_dukien', 'congsuat')
    def tinh_thoi_gian_du_kien(self):
        for rec in self:
            if rec.congsuat > 0 and rec.khoiluong_dukien > 0:
                thoigiandukien = rec.khoiluong_dukien / rec.congsuat
                rec.thoigian_dukien = thoigiandukien
            elif rec.congsuat == 0 and rec.khoiluong_dukien > 0:
                raise ValidationError(_("Nhập công suất cho sản phẩm tương ứng với máy đã xếp."))

    @api.constrains('khoiluong_dukien')
    def _check_positive_khoiluong(self):
        for record in self:
            if record.khoiluong_dukien <= 0:
                raise ValidationError("Khối lượng dự kiến phải lớn hơn 0.")

    @api.depends('khoiluong_dukien', 'khoiluong_thucte')
    def tinh_phan_tram_hoan_thanh(self):
        for rec in self:
            if rec.khoiluong_dukien > 0:
                rec.phantramhoanthanh = rec.khoiluong_thucte / rec.khoiluong_dukien * 100

    @api.depends('khoiluong_thucte')
    def tinh_nang_suat_binh_quan(self):
        for rec in self:
            rec.nangsuatbinhquan = rec.khoiluong_thucte / 22

    def action_gan_lenh(self):
        active_ids = [kh.id for kh in self]
        chon_lenh_form = self.env.ref('mrp_fm.view_chon_lenhsx_form')
        return {
            'name': 'Chọn lệnh',
            'type': 'ir.actions.act_window',
            'res_model': 'ganlenh.sanxuat',
            'view_mode': 'form',
            'view_id': chon_lenh_form.id,
            'target': 'new',
            'context': {
                'active_ids': active_ids,
            }
        }


class GanlenhSanxuat(models.Model):
    _name = 'ganlenh.sanxuat'
    _rec_name = 'lenhsx_ids'

    lenhsx_ids = fields.Many2one('lenh.san.xuat', 'Lệnh sản xuất')

    def trigger_default_lenhsx_ids(self):
        active_ids = self.env.context.get('active_ids')
        kehoachsx = self.env['kehoach.sanxuat'].browse(active_ids)  # Lấy ra bản ghi kehoach.sanxuat đã chọn
        # Cập nhật lệnh sản xuất vào các bản ghi kế hoạch sản xuất
        for rec in kehoachsx:
            rec.lenhsx_ids = self.lenhsx_ids
        # Thông báo gắn lệnh sản xuất thành công
        return self.thong_bao_thanh_cong()

    def thong_bao_thanh_cong(self):
        message_success = self.env.ref('mrp_fm.message_success_gan_lenh_form_view')
        return {
            'name': 'Thông báo',
            'type': 'ir.actions.act_window',
            'res_model': 'ganlenh.sanxuat',
            'view_mode': 'form',
            'view_id': message_success.id,
            'target': 'new',
        }

    def reload_list_view(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
