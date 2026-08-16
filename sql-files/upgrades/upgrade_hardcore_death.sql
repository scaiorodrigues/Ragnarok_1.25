-- ========================================
-- Hardcore Death System
-- Fase 3: Morte permanente + Guardian Angel + Osiris Limbo
-- ========================================

USE ragnarok;

-- Adicionar campos hardcore na tabela char
ALTER TABLE `char`
  ADD COLUMN IF NOT EXISTS `hardcore_dead` TINYINT(1) NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS `guardian_angel_used` TINYINT(1) NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS `osiris_resurrect_time` BIGINT NOT NULL DEFAULT 0;

-- Nota: O campo `osiris_resurrect_time` armazena o timestamp Unix
-- de quando o Limbo de Osiris termina (0 = sem limbo ativo).
