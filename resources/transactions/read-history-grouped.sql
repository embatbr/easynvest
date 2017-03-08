SELECT
    A.year,
    A.valor_venda,
    B.valor_resgate
FROM
(
    SELECT
        to_char(expire_at, 'YYYY') AS year,
        sum(amount) AS valor_venda
    FROM
        tesouro_direto_series
    WHERE
        category = '{0}'
        AND expire_at >= '{1}'
        AND expire_at <= '{2}'
        AND action = 'VENDA'
    GROUP BY
        year
    ORDER BY
        year
) A
JOIN
    (
        SELECT
            to_char(expire_at, 'YYYY') AS year,
            sum(amount) AS valor_resgate
        FROM
            tesouro_direto_series
        WHERE
            category = '{0}'
            AND expire_at >= '{1}'
            AND expire_at <= '{2}'
            AND action = 'RESGATE'
        GROUP BY
            year
        ORDER BY
            year
    ) B
ON
    A.year = B.year;