CREATE TABLE IF NOT EXISTS critters(
    critter_id INTEGER NOT NULL,
    experiment_id INTEGER NOT NULL,
    generation INTEGER NOT NULL,
    species_id INTEGER NOT NULL,
    food_eaten NUMBER,
    fitness NUMBER,
    adjusted_fitness NUMBER,
    PRIMARY KEY (critter_id, experiment_id, generation)
);