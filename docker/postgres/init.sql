CREATE TABLE IF NOT EXISTS videos (
    id SERIAL PRIMARY KEY,
    original_filename VARCHAR(127) NOT NULL,       -- Как файл назывался у пользователя (video.mp4)
    internal_filename VARCHAR(64) UNIQUE NOT NULL, -- Как файл лежит на диске (1f4iciph.mp4) - УНИКАЛЬНОЕ!
    status VARCHAR(16) NOT NULL DEFAULT 'processing',
	message VARCHAR(127),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_videos_internal ON videos(internal_filename);


CREATE TABLE IF NOT EXISTS execution_logs (
    run_id VARCHAR(50) PRIMARY KEY,
    video_id INT NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS 
 $BODY$ BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
 $BODY$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS set_timestamp ON videos;

CREATE TRIGGER set_timestamp
BEFORE UPDATE ON videos
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();