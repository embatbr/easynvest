BEGIN;


DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'category_type') THEN
        CREATE TYPE category_type AS ENUM (
            'LTN',
            'LFT',
            'NTN-B',
            'NTN-B Principal',
            'NTN-C',
            'NTN-F'
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'action_type') THEN
        CREATE TYPE action_type AS ENUM (
            'VENDA',
            'RESGATE');
    END IF;
END$$;


CREATE TABLE IF NOT EXISTS category_ids (
    id              SERIAL          NOT NULL,
    category        category_type   NOT NULL,

    PRIMARY KEY (id),
    UNIQUE (category)
);

TRUNCATE TABLE category_ids;

INSERT INTO category_ids (category) VALUES
    ('LTN'),
    ('LFT'),
    ('NTN-B'),
    ('NTN-B Principal'),
    ('NTN-C'),
    ('NTN-F');


CREATE TABLE IF NOT EXISTS tesouro_direto_series (
    category        category_type                   NOT NULL,
    action          action_type                     NOT NULL,
    expire_at       TIMESTAMP WITHOUT TIME ZONE     NOT NULL,
    amount          MONEY                           NOT NULL,

    PRIMARY KEY (category, action, expire_at)
);


COMMIT;