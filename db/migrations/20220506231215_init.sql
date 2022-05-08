-- migrate:up
CREATE TABLE public.ticker (
	"name" varchar NOT NULL,
    first_timestamp bigint NOT NULL DEFAULT 0,
    last_timestamp bigint NOT NULL DEFAULT 0,
    price bigint not null DEFAULT 0,
	CONSTRAINT ticker_pk PRIMARY KEY ("name")
);

CREATE TABLE public.ticker_state (
	id serial8 NOT NULL,
	ticker_pk varchar NOT NULL,
	price bigint NOT NULL DEFAULT 0,
	ts bigint NOT NULL,
	CONSTRAINT ticker_state_pk PRIMARY KEY (id),
	CONSTRAINT ticker_state_fk FOREIGN KEY (ticker_pk) REFERENCES public.ticker("name") ON DELETE CASCADE
);

CREATE INDEX ticker_state_ts_idx ON public.ticker_state using brin (ts);

CREATE OR REPLACE FUNCTION update_ticker_counter() RETURNS TRIGGER AS $$
    BEGIN
        IF (TG_OP = 'INSERT') THEN
            update public.ticker set last_timestamp=new.ts, price=new.price where new.ticker_pk = public.ticker.name;
            RETURN NEW;
        END IF;
        RETURN NULL;
    END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_counter
    AFTER INSERT
    ON public.ticker_state
    FOR EACH ROW
    EXECUTE PROCEDURE public.update_ticker_counter();



-- migrate:down
DROP TRIGGER update_counter ON public.ticker_state;
drop table public.ticker_state;
drop table public.ticker cascade;
drop FUNCTION update_ticker_counter;
