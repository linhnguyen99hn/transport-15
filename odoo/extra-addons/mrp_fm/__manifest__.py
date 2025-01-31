# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

{
    "name": "Mrp FM",
    "version": "15.0",
    "author": "hungtv2012@gmail.com",
    "sequence": "8",
    "license": "LGPL-3",
    "category": "Hidden",
    # 'assets': {
    #     'web.assets_common': [
    #         '/mrp_fm/static/src/js/gantt_chart.js'
    #     ],
    #     'web.assets_backend': [
    #         '/mrp_fm/static/src/js/d3.min.js'
    #     ],
    #     'web.assets_frontend': [
    #         '/mrp_fm/static/src/js/d3.min.js'
    #     ],
    # },
    "depends": ['base', 'web', 'web_timeline'],
    "data": [
        # 'data/mrp_fm_assets.xml',
        'data/ir_sequence.xml',
        'security/mrp_fm.xml',
        'security/ir.model.access.csv',
        'views/fm_paper_format.xml',
        'views/mrp_fm_view.xml',
        'views/dm_sanpham_view.xml',
        'views/dm_quycach_view.xml',
        'views/don_hang_view.xml',
        'views/nguyenlieu.xml',
        'views/nhomnguyenlieu.xml',
        'views/cong_thuc_phoi_tron.xml',
        'views/dm_may_view.xml',
        'views/dm_khach_view.xml',
        'views/kehoachsanxuat_view.xml',
        'views/donhang_chitiet_lapkh.xml',
        'views/lap_ke_hoach.xml',
        'views/view_chi_tiet_don_hang.xml',
        'wizard/bao_cao_tong_nhu_cau_nguyen_lieu.xml',
        'wizard/bao_cao_tong_nhu_cau_nguyen_lieu_document.xml',
        'wizard/bao_cao_ket_qua_sx.xml',
        'wizard/bao_cao_ket_qua_sx_document.xml',
        'views/don_vi_tinh.xml',
        'views/bang_gia.xml',
        'views/don_gia_luong.xml',
        'views/thong_ke.xml',
        'views/settings.xml',
        'views/lenh_sx.xml',
        'wizard/bao_cao_sx.xml',
        'wizard/bao_cao_danh_gia_hieu_qua.xml',
        'wizard/bao_cao_danh_gia_hieu_qua_document.xml',
        'wizard/bao_cao_thoi_gian_lang_phi.xml',
        'report/lenh_san_xuat.xml',
        'report/lenh_san_xuat_document.xml',
        'report/in_quyet_toan.xml',
        'report/in_quyet_toan_document.xml',
        'views/tinh_tien_ke_hoach.xml',
        # 'views/nhiet_do.xml',
        'report/lenh_tao_hat.xml',
        'report/lenh_tao_hat_document.xml',
        'report/lenh_xuat_nguyen_vat_lieu_view.xml',
        'report/lenh_xuat_nguyen_vat_lieu_document.xml',
        'report/lenh_tron_lieu.xml',
        'report/lenh_tron_lieu_document.xml',
        'wizard/bao_cao_ke_hoach.xml',
        'wizard/bao_cao_ke_hoach_document.xml',
        'report/lenh_premix.xml',
        'report/lenh_premix_document.xml',
        'report/quy_cach_dong_goi_va_hoan_thien_view.xml',
        'report/quy_cach_dong_goi_va_hoan_thien_document.xml',
        'wizard/bao_cao_chi_phi.xml',
        'wizard/bao_cao_chi_phi_document.xml',
        'wizard/bao_cao_tong_chi_phi.xml',
        'wizard/bao_cao_tong_chi_phi_document.xml',
        'wizard/bao_cao_bang_gia.xml',
        'wizard/bao_cao_bang_gia_document.xml',
        'wizard/bao_cao_cong_thuc_phoi_tron.xml',
        'wizard/bao_cao_cong_thuc_phoi_tron_document.xml',
        'wizard/bao_cao_thong_tin_sp.xml',
        'wizard/bao_cao_thong_tin_sp_document.xml',
        'wizard/bao_cao_phan_bo_ke_hoach.xml',
        'wizard/bao_cao_phan_bo_ke_hoach_document.xml',
        'wizard/bao_cao_vat_tu.xml',
        'wizard/bao_cao_vat_tu_document.xml',
        'report/bao_cao_nguyen_lieu_xuat.xml',
        'report/bao_cao_nguyen_lieu_xuat_document.xml',
    ],
    "installable": True,
    'application': True,
    "maintainers": ["hungtv2012@gmail.com"],
    'auto-install': False,
}
