-- Function to notify changes
CREATE OR REPLACE FUNCTION notify_activity_changes()
RETURNS trigger AS $$
BEGIN
    PERFORM pg_notify('activity_changes', json_build_object(
        'operation', TG_OP,
        'id', NEW.id,
        'action', NEW.title,
        'cat_id', NEW."catId",
        'camera_id', NEW."cameraId"
    )::text);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for insert operations
DROP TRIGGER IF EXISTS activity_notify_insert ON activity;
CREATE TRIGGER activity_notify_insert
    AFTER INSERT ON activity
    FOR EACH ROW
    EXECUTE FUNCTION notify_activity_changes();

-- Trigger for update operations
DROP TRIGGER IF EXISTS activity_notify_update ON activity;
CREATE TRIGGER activity_notify_update
    AFTER UPDATE ON activity
    FOR EACH ROW
    EXECUTE FUNCTION notify_activity_changes();
