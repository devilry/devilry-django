CREATE OR REPLACE FUNCTION devilry__largest_datetime(
    param_datetime1 timestamp with time zone,
    param_datetime2 timestamp with time zone)
RETURNS timestamp with time zone AS $$
BEGIN
    IF param_datetime1 IS NULL THEN
        RETURN param_datetime2;
    END IF;
    IF param_datetime2 IS NULL THEN
        RETURN param_datetime1;
    END IF;
    IF param_datetime1 > param_datetime2 THEN
        RETURN param_datetime1;
    END IF;
    return param_datetime2;
END
$$ LANGUAGE plpgsql;
