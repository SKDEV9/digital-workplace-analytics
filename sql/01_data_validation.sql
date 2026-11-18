-- ============================================================================
-- PROJETO: Digital Workplace Analytics
-- ARQUIVO: 01_data_validation.sql
-- OBJETIVO: Auditoria de integridade, granularidade e regras temporais
-- ============================================================================
-- 1. Consistência de volumetria (contagem de linhas por tabela)
SELECT
    'departments' AS tabela,
    COUNT(*) AS total_registros
FROM
    departments
UNION
ALL
SELECT
    'digital_tools',
    COUNT(*)
FROM
    digital_tools
UNION
ALL
SELECT
    'employees',
    COUNT(*)
FROM
    employees
UNION
ALL
SELECT
    'tool_access',
    COUNT(*)
FROM
    tool_access
UNION
ALL
SELECT
    'usage_events',
    COUNT(*)
FROM
    usage_events
UNION
ALL
SELECT
    'support_tickets',
    COUNT(*)
FROM
    support_tickets
UNION
ALL
SELECT
    'training_records',
    COUNT(*)
FROM
    training_records;

-- 2. Auditoria de duplicatas na granularidade de usage_events (deve retornar 0 linhas)
SELECT
    employee_id,
    tool_id,
    usage_date,
    COUNT(*) AS ocorrencias
FROM
    usage_events
GROUP BY
    employee_id,
    tool_id,
    usage_date
HAVING
    COUNT(*) > 1;

-- 3. Regra temporal crítica: uso registrado fora da janela válida de acesso (deve retornar 0)
-- Nota: A FK composta garante que o acesso existe, mas não valida as datas!
SELECT
    COUNT(*) AS eventos_fora_janela_acesso
FROM
    usage_events u
    JOIN tool_access a ON u.employee_id = a.employee_id
    AND u.tool_id = a.tool_id
WHERE
    u.usage_date < a.access_granted_date
    OR (
        a.access_revoked_date IS NOT NULL
        AND u.usage_date > a.access_revoked_date
    );

-- 4. Regra temporal: acesso concedido antes da contratação ou do lançamento da ferramenta (deve retornar 0)
SELECT
    COUNT(*) AS acessos_temporais_invalidos
FROM
    tool_access a
    JOIN employees e ON a.employee_id = e.employee_id
    JOIN digital_tools t ON a.tool_id = t.tool_id
WHERE
    a.access_granted_date < e.hire_date
    OR a.access_granted_date < t.launch_date;

-- 5. Auditoria de chamados em aberto (resolved_at NULL é legítimo, esperado ~12%)
SELECT
    COUNT(*) AS total_chamados,
    COUNT(resolved_at) AS chamados_resolvidos,
    COUNT(*) - COUNT(resolved_at) AS chamados_em_aberto,
    ROUND(
        (
            (COUNT(*) - COUNT(resolved_at)) :: NUMERIC / COUNT(*)
        ) * 100,
        2
    ) AS pct_em_aberto
FROM
    support_tickets;