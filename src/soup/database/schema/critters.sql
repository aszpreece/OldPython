CREATE TABLE IF NOT EXISTS critters(
    critter_id INTEGER NOT NULL,
    experiment_id INTEGER NOT NULL,
    generation INTEGER NOT NULL,
    species_id INTEGER NOT NULL,
    food_eaten FLOAT,
    fitness FLOAT,
    adjusted_fitness FLOAT,
    CONSTRAINT pk_CritterId PRIMARY KEY (critter_id, experiment_id)
);