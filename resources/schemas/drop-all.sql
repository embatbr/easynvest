BEGIN;


DROP TABLE IF EXISTS tesouro_direto_series;

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'action_type') THEN
        DROP TYPE action_type;
    END IF;

    IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'category_type') THEN
        DROP TYPE category_type;
    END IF;
END$$;


COMMIT;