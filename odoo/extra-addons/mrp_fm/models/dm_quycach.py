from odoo import _, api, fields, models, SUPERUSER_ID, tools
from odoo.exceptions import ValidationError, UserError


class DmQuycach(models.Model):
    _name = "dm.quycach"
    _rec_name = 'maquycach'

    maquycach = fields.Char('Mã quy cách')
    tenquycach = fields.Char('Tên quy cách')
    nhomquycach = fields.Many2one('dm.nhomquycach', string='Nhóm quy cách', ondelete='cascade')

    mota = fields.Text('Mô tả')

class DmNhomquycach(models.Model):
    _name = 'dm.nhomquycach'
    _rec_name = 'manhom'

    manhom = fields.Char('Mã nhóm')
    tennhom = fields.Char('Tên nhóm')

    mota = fields.Text('Mô tả')