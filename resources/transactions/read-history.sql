SELECT
    to_char(A.expire_at, 'MM') AS month,
    to_char(A.expire_at, 'YYYY') AS year,
    A.amount AS valor_venda,
    B.amount AS valor_resgate
FROM
    tesouro_direto_series A
JOIN
    (
        SELECT
            amount,
            category,
            action,
            expire_at
        FROM
            tesouro_direto_series
        WHERE
            action = 'RESGATE'
    ) B
ON
    A.category = B.category
    AND A.expire_at = B.expire_at
WHERE
    A.category = '{}'
    AND A.expire_at >= '{}'
    AND A.expire_at <= '{}'
    AND A.action = 'VENDA'
ORDER BY
    year,
    month;