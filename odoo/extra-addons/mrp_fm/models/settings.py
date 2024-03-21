from odoo import models, fields, api, _


class MrpFmSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sophutlapkehoach = fields.Float('Số phút lập kế hoạch')
    sogiochuyendoi = fields.Float('Số giờ chuyển đổi')
    sogiolamviec = fields.Float('Số giờ làm việc')
    tphtkh = fields.Char('TP HTKH')
    tpsanxuat = fields.Char('TP Sản Xuất')
    gdcongnghe = fields.Char('GĐ Công Nghệ')
    tpcongnghe = fields.Char('TP Công Nghệ')
    tonggiamdoc = fields.Char('Tổng Giám Đốc')
    tttsanxuat = fields.Char('TT Tổ Sản Xuất')
    ketoan = fields.Char('Kế Toán')
    ttpremix = fields.Char('TT Premix')
    psale = fields.Char('P Sale')
    bophandonggoi = fields.Char('Bộ Phận Đóng Gói')
    bophanhoanthien = fields.Char('Bộ Phận Hoàn Thiện')
    truongcasx = fields.Char('Trưởng Ca Sản Xuất')
    gdsanxuat = fields.Char('Giám Đốc Sản Xuất')
    tentonggiamdoc = fields.Char('Tên tổng giám đốc')
    tentpsanxuat = fields.Char("Tên TP Sản Xuất")
    tenttpremix = fields.Char("Tên TT Premix")
    tengdcongnghe = fields.Char("Tên GĐ Công Nghệ")
    tenketoan = fields.Char("Tên kế toán")
    tengdsanxuat = fields.Char("Tên Giám Đốc Sản Xuất")
    tentpcongnghe = fields.Char("Tên TP Công Nghệ")
    tentphtkh = fields.Char("Tên TP Hỗ trợ KH")
    tenphongsale = fields.Char("Tên phòng sale")
    tenbophandonggoi = fields.Char("Tên bộ phận đóng gói")
    tenbophanhoanthien = fields.Char("Tên bộ phận hoàn thiện")
    tentruongcasx = fields.Char("Tên Trưởng Ca Sản Xuất")
    tennguoilap = fields.Char("Tên người lập")

    def set_values(self):
        res = super(MrpFmSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('MrpFm.sophutlapkehoach', self.sophutlapkehoach)
        self.env['ir.config_parameter'].set_param('MrpFm.sogiochuyendoi', self.sogiochuyendoi)
        self.env['ir.config_parameter'].set_param('MrpFm.sogiolamviec', self.sogiolamviec)
        self.env['ir.config_parameter'].set_param('MrpFm.tphtkh', self.tphtkh)
        self.env['ir.config_parameter'].set_param('MrpFm.tpsanxuat', self.tpsanxuat)
        self.env['ir.config_parameter'].set_param('MrpFm.gdcongnghe', self.gdcongnghe)
        self.env['ir.config_parameter'].set_param('MrpFm.tpcongnghe', self.tpcongnghe)
        self.env['ir.config_parameter'].set_param('MrpFm.tonggiamdoc', self.tonggiamdoc)
        self.env['ir.config_parameter'].set_param('MrpFm.tttsanxuat', self.tttsanxuat)
        self.env['ir.config_parameter'].set_param('MrpFm.ketoan', self.ketoan)
        self.env['ir.config_parameter'].set_param('MrpFm.ttpremix', self.ttpremix)
        self.env['ir.config_parameter'].set_param('MrpFm.psale', self.psale)
        self.env['ir.config_parameter'].set_param('MrpFm.bophandonggoi', self.bophandonggoi)
        self.env['ir.config_parameter'].set_param('MrpFm.bophanhoanthien', self.bophanhoanthien)
        self.env['ir.config_parameter'].set_param('MrpFm.truongcasx', self.truongcasx)
        self.env['ir.config_parameter'].set_param('MrpFm.gdsanxuat', self.gdsanxuat)
        self.env['ir.config_parameter'].set_param('MrpFm.tentonggiamdoc', self.tentonggiamdoc)
        self.env['ir.config_parameter'].set_param('MrpFm.tentpsanxuat', self.tentpsanxuat)
        self.env['ir.config_parameter'].set_param('MrpFm.tenttpremix', self.tenttpremix)
        self.env['ir.config_parameter'].set_param('MrpFm.tengdcongnghe', self.tengdcongnghe)
        self.env['ir.config_parameter'].set_param('MrpFm.tenketoan', self.tenketoan)
        self.env['ir.config_parameter'].set_param('MrpFm.tengdsanxuat', self.tengdsanxuat)
        self.env['ir.config_parameter'].set_param('MrpFm.tentphtkh', self.tentphtkh)
        self.env['ir.config_parameter'].set_param('MrpFm.tenphongsale', self.tenphongsale)
        self.env['ir.config_parameter'].set_param('MrpFm.tenbophandonggoi', self.tenbophandonggoi)
        self.env['ir.config_parameter'].set_param('MrpFm.tenbophanhoanthien', self.tenbophanhoanthien)
        self.env['ir.config_parameter'].set_param('MrpFm.tentruongcasx', self.tentruongcasx)
        self.env['ir.config_parameter'].set_param('MrpFm.tentpcongnghe', self.tentpcongnghe)
        self.env['ir.config_parameter'].set_param('MrpFm.tennguoilap', self.tennguoilap)
        return res

    @api.model
    def get_values(self):
        res = super(MrpFmSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        res.update({
            'sophutlapkehoach': ICPSudo.get_param('MrpFm.sophutlapkehoach'),
            'sogiochuyendoi': ICPSudo.get_param('MrpFm.sogiochuyendoi'),
            'sogiolamviec': ICPSudo.get_param('MrpFm.sogiolamviec'),
            'tphtkh': ICPSudo.get_param('MrpFm.tphtkh'),
            'tpsanxuat': ICPSudo.get_param('MrpFm.tpsanxuat'),
            'gdcongnghe': ICPSudo.get_param('MrpFm.gdcongnghe'),
            'tpcongnghe': ICPSudo.get_param('MrpFm.tpcongnghe'),
            'tonggiamdoc': ICPSudo.get_param('MrpFm.tonggiamdoc'),
            'tttsanxuat': ICPSudo.get_param('MrpFm.tttsanxuat'),
            'ketoan': ICPSudo.get_param('MrpFm.ketoan'),
            'ttpremix': ICPSudo.get_param('MrpFm.ttpremix'),
            'psale': ICPSudo.get_param('MrpFm.psale'),
            'bophandonggoi': ICPSudo.get_param('MrpFm.bophandonggoi'),
            'bophanhoanthien': ICPSudo.get_param('MrpFm.bophanhoanthien'),
            'truongcasx': ICPSudo.get_param('MrpFm.truongcasx'),
            'gdsanxuat': ICPSudo.get_param('MrpFm.gdsanxuat'),
            'tentonggiamdoc': ICPSudo.get_param('MrpFm.tentonggiamdoc'),
            'tentpsanxuat': ICPSudo.get_param('MrpFm.tentpsanxuat'),
            'tenttpremix': ICPSudo.get_param('MrpFm.tenttpremix'),
            'tengdcongnghe': ICPSudo.get_param('MrpFm.tengdcongnghe'),
            'tenketoan': ICPSudo.get_param('MrpFm.tenketoan'),
            'tengdsanxuat': ICPSudo.get_param('MrpFm.tengdsanxuat'),
            'tentphtkh': ICPSudo.get_param('MrpFm.tentphtkh'),
            'tenphongsale': ICPSudo.get_param('MrpFm.tenphongsale'),
            'tenbophandonggoi': ICPSudo.get_param('MrpFm.tenbophandonggoi'),
            'tenbophanhoanthien': ICPSudo.get_param('MrpFm.tenbophanhoanthien'),
            'tentruongcasx': ICPSudo.get_param('MrpFm.tentruongcasx'),
            'tentpcongnghe': ICPSudo.get_param('MrpFm.tentpcongnghe'),
            'tennguoilap': ICPSudo.get_param('MrpFm.tennguoilap'),
        })
        return res
