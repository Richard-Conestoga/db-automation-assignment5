USE nyc311;

-- B-tree indexes
CREATE INDEX idx_created_date
ON service_requests (created_date);

CREATE INDEX idx_borough
ON service_requests (borough);

CREATE INDEX idx_borough_created
ON service_requests (borough, created_date);

-- FULLTEXT indexes on VARCHAR columns (supported in InnoDB)
CREATE FULLTEXT INDEX idx_ft_descriptor
ON service_requests (descriptor);

CREATE FULLTEXT INDEX idx_ft_desc_complaint
ON service_requests (descriptor, complaint_type);