from odoo import models, fields, api
from odoo.osv import expression


class BaoCaoPhanBoKeHoach(models.TransientModel):
    _name = 'bao.cao.phan.bo.ke.hoach'
    _rec_name = 'date_start'

    date_start = fields.Date(string='Start Date')
    date_end = fields.Date(string='End Date')
    maychay = fields.Many2one('dm.may', 'Máy chạy')
    lenhsx = fields.Many2one('lenh.san.xuat', 'Lệnh sản xuất')
    donhang = fields.Many2one('don.hang', 'Đơn hàng')
    sanpham = fields.Many2one('dm.sanpham', 'Sản phẩm')

    def gen_report(self):
        date_start = self.date_start
        date_end = self.date_end
        domain = []
        if self.date_start:
            domain = expression.AND([domain, [('ngay', '>=', self.date_start)]])
            # date_start = date_start.strftime('%d/%m/%Y')
        if self.date_end:
            domain = expression.AND([domain, [('ngay', '<=', self.date_end)]])
            # date_end = date_end.strftime('%d/%m/%Y')
        if self.maychay:
            domain = expression.AND([domain, [('kh_may_id.id', '=', self.maychay.id)]])
        if self.lenhsx:
            domain = expression.AND([domain, [('lenhsx_ids.id', '=', self.lenhsx.id)]])
        if self.donhang:
            domain = expression.AND([domain, [('donhang', '=', self.donhang.id)]])
        if self.sanpham:
            domain = expression.AND([domain, [('sanpham', '=', self.sanpham.id)]])
        domain = expression.AND([domain, [('khoiluong_dukien', '>', 0)]])
        domain = expression.AND([domain, [('ngay', '<>', False)]])
        data = {
            'model': self._name,
            'ids': self.ids,
            'form': {
                'date_start': date_start, 'date_end': date_end, 'domain': domain, 'donhang': self.donhang,
                'may': self.maychay.mamay,
                'sanpham': self.sanpham, 'madonhang': self.donhang.madonhang, 'tensanpham': self.sanpham.tensanpham,
                'lenhsx': self.lenhsx.lenhsx
            },
        }
        action = self.env.ref('mrp_fm.action_bao_cao_phan_bo_ke_hoach').report_action(self, data=data)
        return action


class BaoCaoKeHoachPhanBo(models.AbstractModel):
    _name = 'report.mrp_fm.bao_cao_phan_bo_ke_hoach_document'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        lenhsx = data['form']['lenhsx']
        may = data['form']['may']
        sanpham = data['form']['sanpham']
        tensanpham = data['form']['tensanpham']
        donhang = data['form']['donhang']
        madonhang = data['form']['madonhang']
        domain = data['form']['domain']

        sorted_docs = self.env['kehoach.sanxuat'].search(domain, order="ngay asc")
        docs = sorted_docs.sorted(key=lambda o: o.ngay)
        # order không có tác dụng, trong template phải sử dụng <t t-foreach="sorted(list(set(group1)))" t-as="g1">

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start,
            'date_end': date_end,
            'may': may,
            'lenhsx': lenhsx,
            'sanpham': sanpham,
            'tensanpham': tensanpham,
            'donhang': donhang,
            'madonhang': madonhang,
            'docs': docs,
        }
