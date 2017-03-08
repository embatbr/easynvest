SELECT
    to_char(expire_at, 'YYYY') AS year,
    to_char(expire_at, 'MM') AS month,
    amount
FROM
    tesouro_direto_series
WHERE
    action = '{}'
    AND category = '{}'
    AND expire_at >= '{}'
    AND expire_at <= '{}'
ORDER BY
    year,
    month;