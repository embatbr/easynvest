SELECT
    to_char(expire_at, 'YYYY') AS year,
    sum(amount)
FROM
    tesouro_direto_series
WHERE
    action = '{}'
    AND category = '{}'
    AND expire_at >= '{}'
    AND expire_at <= '{}'
GROUP BY
    year
ORDER BY
    year;