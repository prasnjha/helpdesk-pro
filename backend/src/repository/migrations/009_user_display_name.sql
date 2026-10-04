-- Display names for users, used by log redaction (NFR-03). All names are synthetic.
ALTER TABLE users ADD COLUMN display_name TEXT;

UPDATE users SET display_name = 'Priya Raman' WHERE id = 'C-1';
UPDATE users SET display_name = 'Tomas Vale' WHERE id = 'C-2';
UPDATE users SET display_name = 'Dana Whitfield' WHERE id = 'AG-1';
UPDATE users SET display_name = 'Leon Brisco' WHERE id = 'AG-2';
UPDATE users SET display_name = 'Maren Okafor' WHERE id = 'AD-1';
