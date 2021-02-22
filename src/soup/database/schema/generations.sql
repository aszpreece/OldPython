CREATE TABLE IF NOT EXISTS generations (
    generation_num INTEGER NOT NULL,
    experiment_id INTEGER NOT NULL,
    PRIMARY KEY (generation_num, experiment_id),
    CONSTRAINT fk_experiment_generation FOREIGN KEY (experiment_id) REFERENCES experiments(id)
);