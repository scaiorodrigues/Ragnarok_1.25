-- [Hardcore] Adicionar colunas na tabela `char`
-- Execute este arquivo no banco 'ragnarok' com um usuario com privilegios ALTER TABLE.
--
-- Uso: mysql -u root -p ragnarok < hardcore_columns.sql
--   ou cole no MySQL Workbench / phpMyAdmin

USE ragnarok;

-- Verificar e adicionar cada coluna apenas se nao existir
-- (MySQL 8.0+ suporta IF NOT EXISTS no ADD COLUMN)

ALTER TABLE `char`
  ADD COLUMN IF NOT EXISTS `hardcore_dead`         TINYINT(1)  NOT NULL DEFAULT 0  COMMENT 'Personagem morto permanentemente (permadeath)',
  ADD COLUMN IF NOT EXISTS `guardian_angel_used`   TINYINT(1)  NOT NULL DEFAULT 0  COMMENT 'Carta Osiris (Angel Guardian) ja foi usada',
  ADD COLUMN IF NOT EXISTS `osiris_resurrect_time` BIGINT      NOT NULL DEFAULT 0  COMMENT 'Unix timestamp de quando a ressurreicao do Limbo expira';

-- Verificar resultado
SELECT COLUMN_NAME, COLUMN_TYPE, COLUMN_DEFAULT, COLUMN_COMMENT
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'ragnarok'
  AND TABLE_NAME   = 'char'
  AND COLUMN_NAME IN ('hardcore_dead','guardian_angel_used','osiris_resurrect_time')
ORDER BY COLUMN_NAME;
