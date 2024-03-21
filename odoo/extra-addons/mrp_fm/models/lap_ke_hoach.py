from odoo import _, api, fields, models, SUPERUSER_ID, tools
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta, timezone
import calendar
import pytz

class lkh(models.TransientModel):
    _name = 'lkh'

    tz_vn = pytz.timezone('Asia/Ho_Chi_Minh')

    id_dalap = fields.Integer('Id đã lập')
    dh_ct_id = fields.Many2one('donhang.chitiet')
    may_id = fields.Many2one('dm.may')
    ca = fields.Integer('Ca')
    kl_dukien = fields.Float('Khối lượng dự kiến')
    tg_dukien = fields.Float('Thời gian dự kiến (phút)')
    tg_chuyendoi = fields.Float('Thời gian chuyển đổi (phút)')
    congsuatmay = fields.Float('Công suất máy')
    stt = fields.Integer('Số thứ tự')
    tg_batdau = fields.Datetime('Thời gian bắt đầu')
    tg_ketthuc = fields.Datetime('Thời gian kết thúc')

    # -----Các biến của lớp
    tg_lapkehoach = 0.5
    tg_batdauchay = datetime.now()
    tungay = datetime.now().date()
    denngay = datetime.now().date()
    dtKehoach = []
    dtNhucau = []
    ds_may = []
    tongnhucau = 0
    tongnhucaukhoidau = 0
    tongsomay = 0
    tongsoca = 0
    phuongan = 0
    sophutmotca = 12 * 60
    chisothoigian = float('inf')
    dtKetqua = []
    max_chisothoigian = float('inf')

    def lay_tg_lapkehoach(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        lkh.tg_lapkehoach = float(ICPSudo.get_param('MrpFm.sophutlapkehoach'))
        lkh.tg_chuyendoi = float(ICPSudo.get_param('MrpFm.sogiochuyendoi')) * 60
        lkh.sophutmotca = float(ICPSudo.get_param('MrpFm.sogiolamviec')) * 60 # / 2    # ----- 1 ca được tính cả ngày

    def lapkehoach(self):
        try:
            # -----Lấy các tham số về thời gian
            self.lay_tg_lapkehoach()
            # -----Tính nhu cầu lập kế hoạch
            # -----Lọc và sắp xếp đơn hàng chi tiết theo mức độ ưu tiên và ngày giao hàng
            lkh.dtNhucau = [item for item in lkh.dh_chitiet if item['soluongchuacokehoach'] > 0 ]
            lkh.dtNhucau = sorted(lkh.dtNhucau, key=lambda r: (r.donhang_id.mucdouutien, r.ngaygiao.date()))
            for rec in lkh.dtNhucau:
                rec.dasanxuat = 0
            # -----Tạo bảng dtKehoach để sao chép kế hoạch hiện tại vào và bổ sung kế hoạch xây dựng thêm
            lkh.dtKehoach = []
            khdalap = self.env['kehoach.sanxuat'].search([]) # ([('ngay', '>=', lkh.tungay), ('ngay', '<=', lkh.denngay)])
            for r in khdalap:
                if r.ngay:
                    newrec = self.env['lkh'].create({
                        'id_dalap': r.id,
                        'dh_ct_id': r.donhangchitiet_id.id,
                        'may_id': r.kh_may_id.id,
                        'ca': (r.ngay - lkh.tungay).days, # * 2 + r.ca - 1,
                        'kl_dukien': r.khoiluong_dukien,
                        'tg_dukien': r.thoigian_dukien * 60,
                        'tg_chuyendoi': r.thoigian_chuyendoi * 60,
                        'tg_batdau': r.thoigian_batdau,
                        'tg_ketthuc': r.thoigian_ketthuc,
                    })
                    lkh.dtKehoach.append(newrec)
            # -----Lấy danh sách máy đang hoạt động
            lkh.ds_may = self.env['dm.may'].search([('tinhtrang', '=', 'hoatdong')])
            # -----Tính tổng nhu cầu, Tổng số máy, Tổng số ca, Số phương án
            lkh.chisothoigian = lkh.max_chisothoigian
            lkh.stt = 1
            lkh.tongnhucau = 0
            lkh.tongsomay = len(lkh.ds_may)
            lkh.tongsoca = ((lkh.denngay - lkh.tungay).days + 1) # * 2
            for r in lkh.dtNhucau:
                if r.soluongchuacokehoach > 0:
                    lkh.tongnhucau += r.soluongchuacokehoach
            if lkh.tongnhucau == 0:
                # -----Thông báo nhu cầu lập kế hoạch =0
                return
            lkh.tongnhucaukhoidau = lkh.tongnhucau
            # -----Duyệt kế hoạch sản xuất
            lkh.tg_batdauchay = datetime.now()
            self.duyetkehoachsanxuat(0, 0)
            self.ghiketqua()
            return self.thong_bao_thanh_cong()
        except Exception as e:
            raise 'Lỗi lập kế hoạch!'

    def danhgiaketqua(self):
        try:
            cstg = self.tinhchisothoigian()
            if cstg < lkh.chisothoigian:
                lkh.chisothoigian = cstg
                lkh.dtKetqua = []
                for r in lkh.dtKehoach:
                    newrec = self.env['lkh'].create({
                        'id_dalap': r.id_dalap,
                        'dh_ct_id': r.dh_ct_id.id,
                        'may_id': r.may_id.id,
                        'ca': r.ca,
                        'kl_dukien': r.kl_dukien,
                        'tg_dukien': r.tg_dukien,
                        'tg_chuyendoi': r.tg_chuyendoi,
                        'congsuatmay': r.congsuatmay,
                    })
                    lkh.dtKetqua.append(newrec)
        except Exception as e:
            raise 'Lỗi đánh giá kết quả!'

    def tinhchisothoigian(self):
        try:
            chisotg = 0
            for r in lkh.dtNhucau:
                filtered_list = [item for item in lkh.dtKehoach if item['dh_ct_id'].id == r.id]
                sorted_list = sorted(filtered_list, key=lambda x: x['ca'], reverse=True)
                if len(sorted_list) > 0:
                    rec = sorted_list[0]
                    if rec:
                        if lkh.tungay + timedelta(days=rec.ca) > r.ngaygiao.date(): # timedelta(days=rec.ca / 2) > r.ngaygiao.date():
                            chisotg += (lkh.tungay + timedelta(
                                days=rec.ca) - r.ngaygiao.date()).total_seconds() / 360 / 24 * r.soluongchuacokehoach / lkh.tongnhucaukhoidau
                            # days=rec.ca / 2) - r.ngaygiao.date()).total_seconds() / 360 / 24 * r.soluongchuacokehoach / lkh.tongnhucaukhoidau
        except Exception as e:
            raise 'Lỗi tính chỉ số về thời gian đáp ứng kế hoạch giao hàng!'
        return float(chisotg)

    def ghiketqua(self):
        try:
            if lkh.chisothoigian < lkh.max_chisothoigian:
                # -----Thông báo hỏi đáp có đồng ý kế hoạch đã lập không

                # -----Ghi kế hoạch (chèn vào bảng kehoach.sanxuat)
                if len(lkh.dtKetqua) == 0:
                    return
                lkh.dtKetqua = sorted(lkh.dtKetqua, key=lambda r: r.stt)
                for r in lkh.dtKetqua:
                    if r.id_dalap == 0:
                        ngay = lkh.tungay + timedelta(days=r.ca) # / 2)
                        tgian_batdau = datetime.combine(ngay, datetime.min.time())
                        # ----- Xác định thời gian bắt đầu (max thời gian kết thúc của các lệnh trong ca, máy)
                        ngay_batdau = datetime.combine(ngay, datetime.min.time()) - timedelta(hours=7)
                        ngay_ketthuc = ngay_batdau + timedelta(days=1)
                        kehoachdaluu = self.env['kehoach.sanxuat'].search([('thoigian_ketthuc', '>=', ngay_batdau), ('thoigian_ketthuc', '<', ngay_ketthuc)
                                                                              , ('kh_may_id', '=', r.may_id.id)], order='thoigian_ketthuc DESC')
                        if len(kehoachdaluu) > 0:
                            tgian_batdau = kehoachdaluu[0]['thoigian_ketthuc'] + timedelta(hours=7) #+ timedelta(seconds=1)
                        self.env['kehoach.sanxuat'].create({
                            'donhang': r.dh_ct_id.donhang_id.id,
                            'donhangchitiet_id': r.dh_ct_id.id,
                            'sanpham': r.dh_ct_id.mathuongmaisp.id,
                            'kh_may_id': r.may_id.id,
                            'ngay': ngay,
                            # 'ca': ca,
                            'khoiluong_dukien': r.kl_dukien,
                            'thoigian_dukien': r.tg_dukien / 60,
                            'thoigian_chuyendoi': r.tg_chuyendoi / 60,
                            'mucdouutien': r.dh_ct_id.donhang_id.mucdouutien,
                            'thoigian_batdau': tgian_batdau-timedelta(hours=7),
                            'thoigian_ketthuc': tgian_batdau-timedelta(hours=7)
                                                + timedelta(hours=r.tg_dukien/60) + timedelta(hours=r.tg_chuyendoi/60),
                        })
        except Exception as e:
            raise 'Lỗi ghi kết quả!'

    def duyetkehoachsanxuat(self, ca, may):
        try:
            if (datetime.now() - lkh.tg_batdauchay).total_seconds() / 60 > lkh.tg_lapkehoach:
                return
            if (lkh.tungay + timedelta(days=ca)).weekday() == 6: # timedelta(days=ca / 2)).weekday() == 6 and (ca % 2 + 1) == 2:
                self.duyetkehoachsanxuat(ca + 1, 0)
            else:
                if lkh.tongnhucau <= 0:
                    lkh.phuongan += 1
                    self.danhgiaketqua()
                else:
                    if may == lkh.tongsomay:
                        if ca > lkh.tongsoca - 1:
                            lkh.phuongan += 1
                            self.danhgiaketqua()
                        else:
                            self.duyetkehoachsanxuat(ca + 1, 0)
                    else:
                        if self.ktradkmaychay(ca, may):
                            ktra = True
                            for rec in lkh.dtNhucau:
                                tgdabotri = [0]
                                congsuat = [0]
                                tgchuyendoi = [0]
                                if self.ktradksapxep(rec, ca, may, tgdabotri, congsuat, tgchuyendoi):
                                    ktra = False
                                    # -----Thông tin tính kldukien
                                    tgtrong = lkh.sophutmotca - tgdabotri[0] - tgchuyendoi[0]
                                    nhucauconlai = rec.soluongchuacokehoach - rec.dasanxuat
                                    tgconlai = nhucauconlai / congsuat[0] * 60  # lkh.sophutmotca

                                    if tgtrong < 0:
                                        continue

                                    if tgtrong < tgconlai:
                                        kldukien = tgtrong * congsuat[0] / 60  # lkh.sophutmotca
                                        tgdukien = tgtrong + tgchuyendoi[0]
                                    else:
                                        kldukien = nhucauconlai
                                        tgdukien = tgconlai + tgchuyendoi[0]

                                    newrec = self.env['lkh'].create({
                                        'id_dalap': 0,
                                        'dh_ct_id': rec.id,
                                        'may_id': lkh.ds_may[may].id,
                                        'ca': ca,
                                        'kl_dukien': kldukien,
                                        'tg_dukien': tgdukien,
                                        'tg_chuyendoi': tgchuyendoi[0],
                                        'congsuatmay': congsuat[0],
                                        'stt': lkh.stt,
                                    })
                                    lkh.dtKehoach.append(newrec)
                                    rec.dasanxuat += kldukien
                                    lkh.tongnhucau -= kldukien
                                    lkh.stt += 1

                                    if tgdukien == tgtrong:
                                        self.duyetkehoachsanxuat(ca, may + 1)
                                    else:
                                        self.duyetkehoachsanxuat(ca, may)

                                    lkh.stt -= 1
                                    lkh.tongnhucau += kldukien
                                    rec.dasanxuat -= kldukien
                                    lkh.dtKehoach = [item for item in lkh.dtKehoach if not (
                                                item['ca'] == ca and item['may_id'].id == lkh.ds_may[may].id and item[
                                            'dh_ct_id'].id == rec.id)]
                            if ktra:
                                self.duyetkehoachsanxuat(ca, may + 1)
                        else:
                            self.duyetkehoachsanxuat(ca, may + 1)

        except Exception as e:
            raise 'Lỗi duyệt kế hoạch!'

    def ktradkmaychay(self, ca, may):
        try:
            tgdabotri = self.thoigiandabotri(ca, may)
            if tgdabotri >= lkh.sophutmotca:
                return False
        except Exception as e:
            raise 'Lỗi kiểm tra điều kiện chạy máy!'
            return False
        return True

    def ktradksapxep(self, rec, ca, may, tgdabotri, congsuat, tgchuyendoi):
        try:
            # -----Đã sản xuất xong không sắp xếp chạy
            nhucauconlai = rec.soluongchuacokehoach - rec.dasanxuat
            if nhucauconlai <= 0:
                return False
            # -----Công suất = 0 không chạy
            congsuat[0] = 0
            csmay = self.env['congsuat.may'].search([('may_ids.mamay', '=', lkh.ds_may[may].mamay), ('sanpham_ids.id', '=', rec.mathuongmaisp.id)], limit=1)
            if len(csmay) > 0:
                congsuat[0] = csmay[0].congsuat
            if congsuat[0] == 0:
                return False
            else:
                # -----Đã bố trí hết thời gian không chạy tiếp
                tgdabotri[0] = self.thoigiandabotri(ca, may)
                if tgdabotri[0] >= lkh.sophutmotca:
                    return False
            # -----Cùng ca không sản xuất cùng sản phẩm
            records = [item for item in lkh.dtKehoach if (item['ca'] == ca and item['dh_ct_id'].id == rec.id)]
            if len(records) > 0:
                return False
            # -----Ca sau có sản phẩm sản xuất ca trước không sử dụng khác máy
            if ca > 0:
                records = [item for item in lkh.dtKehoach if (item['ca'] == ca-1 and item['dh_ct_id'].id == rec.id and item['may_id'].id != lkh.ds_may[may].id)]
                if len(records) > 0:
                    return False
            # -----Tính thời gian chuyển đổi
            if ca > 0:
                filtered_list = [item for item in lkh.dtKehoach if (item['ca'] == ca-1 and item['may_id'].id == lkh.ds_may[may].id)]
                sorted_list = sorted(filtered_list, key=lambda x: x['stt'], reverse=True)
                if len(sorted_list) > 0:
                    if sorted_list[0]['dh_ct_id'].masx != rec.masx:
                        tgchuyendoi[0] = lkh.tg_chuyendoi
            # -----Kiểm tra thời gian trống nhỏ hơn 0
            if lkh.sophutmotca - tgdabotri[0] - tgchuyendoi[0] <= 0:
                return False

        except Exception as e:
            raise 'Lỗi kiểm tra điều kiện sắp xếp!'
            return False
        return True

    def thoigiandabotri(self, ca, may):
        tgdabotri = 0
        records = [item for item in lkh.dtKehoach if (item['ca'] == ca and item['may_id'].id == lkh.ds_may[may].id)]
        for rec in records:
            tgdabotri += rec.tg_dukien
        return float(tgdabotri)

    # -----Chọn thời gian lập kế hoạch---------------------------
    date_start = fields.Date('Từ ngày')
    date_end = fields.Date('Đến ngày')
    dh_chitiet = []

    def lapkehoachsanxuat(self, dh_chitiet):
        return self.chon_thoi_gian_lapkh(dh_chitiet)
    def chon_thoi_gian_lapkh(self, dh_chitiet):
        lkh.da_chontg = False
        self.date_start = datetime.now()
        # Lấy ngày cuối tháng
        today = datetime.today()
        last_day = calendar.monthrange(today.year, today.month)[1]
        self.date_end = datetime(today.year, today.month, last_day)
        # -----Hiện bảng chọn thời gian
        return self.hien_form_chon_thoi_gian_lap_ke_hoach(dh_chitiet)
    def hien_form_chon_thoi_gian_lap_ke_hoach(self, dh_chitiet):
        donhang_ids = [dh.id for dh in dh_chitiet]
        thoi_gian = self.env.ref('mrp_fm.thoi_gian_lkh_form_view')
        return {
            'name': 'Thời gian lập kế hoạch',
            'type': 'ir.actions.act_window',
            'res_model': 'lkh',
            'view_mode': 'form',
            'view_id': thoi_gian.id,
            'res_id': self.id,
            'target': 'new',
            'context': {
                'donhang_ids': donhang_ids,
            }
        }
    def xac_nhan_thoi_gian_lapkh(self):
        if self.date_start and self.date_end:
            lkh.tungay = self.date_start
            lkh.denngay = self.date_end
            donhang_ids = self.env.context.get('donhang_ids')
            lkh.dh_chitiet = self.env['donhang.chitiet'].browse(donhang_ids)
            return self.lapkehoach()

    # -----Thông báo lập kế hoạch thành công-------------------------------
    def thong_bao_thanh_cong(self):
        message_success = self.env.ref('mrp_fm.message_success_lkh_form_view')
        return {
            'name': 'Thông báo',
            'type': 'ir.actions.act_window',
            'res_model': 'lkh',
            'view_mode': 'form',
            'view_id': message_success.id,
            'target': 'new',
        }
    def reload_list_view(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

