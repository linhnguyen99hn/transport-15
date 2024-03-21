from odoo import models, fields, api


class Baocaovattu(models.TransientModel):
    _name = 'bao.cao.vat.tu'

    @api.depends('create_date')
    def name_get(self):
        result = []
        for record in self:
            name = record.create_date.strftime('%d-%m-%Y')
            result.append((record.id, name))
        return result

    date_start = fields.Date(string='Start Date', required=True)
    date_end = fields.Date(string='End Date', required=True)
    mavattu = fields.Char("Mã vật tư")
    tenvattu = fields.Char("Mã vật tư")
    donvitinh = fields.Char("Đơn vị tính")
    lenhsx = fields.Many2one('lenh.san.xuat', 'Lệnh sản xuất số')
    soluongkehoach = fields.Float("Số lượng kế hoạch")
    vattu_id = fields.Many2one('nguyen.lieu', 'Mã vật tư')

    # @api.depends('vattu_id.mavattu')
    # def _compute_mavattu_id(self):
    #     for record in self:
    #         record.mavattu_id = record.vattu_id.mavattu.id if record.vattu_id else False

    # mavattu_id = fields.Many2one('nguyen.lieu', string='Mã Vật Tư', compute='_compute_mavattu_id', store=True)

    def get_report(self):
        if self.date_start:
            tungay = self.date_start.strftime('%d/%m/%Y')
        if self.date_end:
            dengay = self.date_end.strftime('%d/%m/%Y')
        data = {
            'model': self._name,
            'ids': self.ids,
            'form': {
                'malenhsx': self.lenhsx.id,
                'lenhsx': self.lenhsx.lenhsx,
                'vattu_id': self.vattu_id.id,
                'date_start': self.date_start, 'date_end': self.date_end, 'tungay': tungay, 'denngay': dengay
            },
        }

        action = self.env.ref('mrp_fm.bao_cao_vat_tu').report_action(self, data=data)
        return action


class Baocaovattumau(models.AbstractModel):
    _name = 'report.mrp_fm.bao_cao_vat_tu_document'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        tungay = data['form']['tungay']
        denngay = data['form']['denngay']
        lenhsx = data['form']['lenhsx']
        malenhsx = data['form']['malenhsx']
        vattu_id = data['form']['vattu_id']
        mavattu = self.env['lenh.cap.vat.tu'].search([('lenhsx_id', '=', malenhsx)], limit=1).mavattu
        param = {}
        where_string = ""

        if date_start:
            where_string += " and (khsx.ngay >= %(date_start)s ) "
            param['date_start'] = date_start

        if date_end:
            where_string += " And (khsx.ngay <= %(date_end)s ) "
            param['date_end'] = date_end

        if vattu_id:
            where_string += " And (nl.id = %(vattu_id)s ) "
            param['vattu_id'] = vattu_id



        query = """
            Select nl.manguyenlieu, nl.tennguyenlieu, dvt.donvitinh, sum(vt.soluongkehoach) as soluongkehoach
            From lenh_san_xuat lsx
                LEFT JOIN kehoach_sanxuat khsx ON khsx.lenhsx_ids = lsx.id
                Left Join lenh_cap_vat_tu vt On vt.lenhsx_id=lsx.id
                left join nguyen_lieu nl on vt.mavattu = nl.id
                left join don_vi_tinh dvt on dvt.id=nl.donvitinh
            Where soluongkehoach>0 {where_string}
            Group by nl.manguyenlieu, nl.tennguyenlieu, dvt.donvitinh
            Order by nl.manguyenlieu
        """.format(where_string=where_string, )
        self.env.cr.execute(query, param)
        data_chiphi = self.env.cr.fetchall()
        if data_chiphi:
            _ids = []
            for line in data_chiphi:
                data_row = ({
                    'mavattu': line[0],
                    'tenvattu': line[1],
                    'donvitinh': line[2],
                    'soluongkehoach': line[3],
                    'lenhsx': malenhsx,
                    'date_start': date_start,
                    'date_end': date_end

                })
                _ids.append(self.env['bao.cao.vat.tu'].create(data_row).id)

            docs = self.env['bao.cao.vat.tu'].browse(_ids)

            return {
                'doc_ids': data['ids'],
                'doc_model': data['model'],
                'tungay': tungay,
                'denngay': denngay,
                'lenhsx': lenhsx,
                'docs': docs,
            }
