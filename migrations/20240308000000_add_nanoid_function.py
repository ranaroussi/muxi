#!/usr/bin/env python3
"""
@migration: add_nanoid_function
@generated: 2024-03-08 00:00:00
@description: Adds a nanoid generation function to PostgreSQL
"""


def up() -> str:
    """
    Returns the SQL for the forward migration that adds the nanoid function.

    Returns:
        SQL string to be executed for the up migration
    """
    return """
        -- Migration: Add nanoid function to PostgreSQL
        -- This migration adds a function to generate Nano IDs in PostgreSQL

        -- Enable the pgcrypto extension for gen_random_bytes function
        CREATE EXTENSION IF NOT EXISTS pgcrypto;

        -- Function: nanoid(size int, alphabet text)
        -- Description: Generates a Nano ID of the specified size using the given alphabet
        -- Parameters:
        --   size: Length of the ID to generate (default: 21)
        --   alphabet: Character set to use for the ID (default: URL-friendly characters)
        -- Returns: A string containing the generated Nano ID

        CREATE OR REPLACE FUNCTION nanoid(
            size int DEFAULT 21,
            alphabet text DEFAULT '_-0123456789abcdefghijklmnopqrstuvwxyz'
                                 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        )
            RETURNS text
            LANGUAGE plpgsql
            VOLATILE
        AS
        $$
        DECLARE
            idBuilder      text := '';
            counter        int  := 0;
            bytes          bytea;
            alphabetIndex  int;
            alphabetArray  text[];
            alphabetLength int;
            mask           int;
            step           int;
        BEGIN
            -- Split the alphabet into an array of characters
            alphabetArray := regexp_split_to_array(alphabet, '');
            alphabetLength := array_length(alphabetArray, 1);

            -- Calculate the bitmask for generating random values
            mask := (2 << CAST(FLOOR(LOG(alphabetLength - 1) / LOG(2)) AS int)) - 1;

            -- Calculate step size for generating random bytes
            step := CAST(CEIL(1.6 * mask * size / alphabetLength) AS int);

            -- Generate the ID
            WHILE true LOOP
                -- Get random bytes
                bytes := gen_random_bytes(step);

                -- Process each byte
                WHILE counter < step LOOP
                    alphabetIndex := (get_byte(bytes, counter) & mask) + 1;

                    -- Check if the index is within alphabet bounds
                    IF alphabetIndex <= alphabetLength THEN
                        idBuilder := idBuilder || alphabetArray[alphabetIndex];

                        -- Return the ID once we reach the desired length
                        IF length(idBuilder) = size THEN
                            RETURN idBuilder;
                        END IF;
                    END IF;

                    counter := counter + 1;
                END LOOP;

                counter := 0;
            END LOOP;
        END
        $$;

        -- Add a comment to the function
        COMMENT ON FUNCTION nanoid(int, text) IS 'Generates a Nano ID of the specified size using the given alphabet';

        -- Verify the function is created
        DO $$
        BEGIN
            -- Test the function with default parameters
            PERFORM nanoid();

            -- Log success
            RAISE NOTICE 'nanoid function successfully installed';
        END
        $$;
    """


def down() -> str:
    """
    Returns the SQL for the rollback migration that removes the nanoid function.

    Returns:
        SQL string to be executed for the down migration
    """
    return """
        -- Drop the nanoid function
        DROP FUNCTION IF EXISTS nanoid(int, text);
    """
