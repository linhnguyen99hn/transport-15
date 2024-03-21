CREATE OR REPLACE FUNCTION bang_gia_hieu_luc(ngay date)
RETURNS TABLE (nguyenlieu int, manguyenlieu varchar, tennguyenlieu varchar, tungay date, dongia float)
AS $$
BEGIN
    RETURN QUERY
    SELECT a.nguyenlieu, nl.manguyenlieu, nl.tennguyenlieu, a.tungay, gnl.dongia
    FROM
        (
        SELECT gnl.nguyenlieu, max(bg.tungay) AS tungay
        FROM gia_nguyen_lieu gnl 
            LEFT JOIN bang_gia bg ON gnl.bang_gia_ids = bg.id
        WHERE coalesce(gnl.nguyenlieu, 0) <> 0
            AND bg.tungay <= ngay
        GROUP BY gnl.nguyenlieu
        ) AS a 
        LEFT JOIN bang_gia bg ON a.tungay = bg.tungay
        LEFT JOIN gia_nguyen_lieu gnl ON a.nguyenlieu = gnl.nguyenlieu AND gnl.bang_gia_ids = bg.id
        LEFT JOIN nguyen_lieu nl ON a.nguyenlieu = nl.id
    ORDER BY a.nguyenlieu;

END;
$$ LANGUAGE plpgsql;


--Drop Function bang_gia_hieu_luc
--SELECT * FROM bang_gia_hieu_luc('2024-02-15');
