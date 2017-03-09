SELECT
    to_char(expire_at, 'YYYY') AS year,
    to_char(expire_at, 'MM') AS month,
    id,
    category,
    action,
    amount
FROM
    tesouro_direto_series
WHERE
    expire_at >= '{}'
    AND expire_at <= '{}'
    AND id IN ({});