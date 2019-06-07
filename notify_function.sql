CREATE FUNCTION notify_trigger() RETURNS trigger AS $$
DECLARE
BEGIN
    PERFORM pg_notify('watch_realtime_table', row_to_json(NEW)::text);
    RETURN new;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER watch_realtime_table_trigger AFTER INSERT ON realtime_table
FOR EACH ROW EXECUTE PROCEDURE notify_trigger();