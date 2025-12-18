-- ============================================================
-- 1. TABELA DE MAPEAMENTO (Organização <-> Variável)
-- ============================================================
CREATE TABLE organization_mappings (
    id SERIAL PRIMARY KEY,
    organizacao TEXT NOT NULL UNIQUE,  -- Nome Real (ex: Coca Cola)
    variavel TEXT NOT NULL UNIQUE      -- Token (ex: FORNECEDOR_1)
);

-- Popular a tabela com os dados do seu projeto
INSERT INTO organization_mappings (organizacao, variavel) VALUES
    -- Fornecedores
    ('Coca Cola', 'FORNECEDOR_1'),
    ('Nestlé Brasil', 'FORNECEDOR_2'),
    ('M Dias Branco', 'FORNECEDOR_3'),
    ('Vivo', 'FORNECEDOR_4'),
    
    -- Varejistas
    ('Grupo Pão de Açúcar', 'VAREJISTA_1'),
    ('Carrefour', 'VAREJISTA_2'),
    ('Açaí Atacadista', 'VAREJISTA_3'),
    ('Dia', 'VAREJISTA_4');


-- ============================================================
-- 2. TABELA DE DESCONTOS REALIZADOS
-- (O que de fato aconteceu nas notas fiscais)
-- ============================================================
CREATE TABLE descontos_realizados (
    id SERIAL PRIMARY KEY,
    fornecedor TEXT NOT NULL REFERENCES organization_mappings(variavel), -- Link seguro
    varejista TEXT NOT NULL REFERENCES organization_mappings(variavel),  -- Link seguro
    data_operacao DATE NOT NULL,
    valor_desconto DECIMAL(10, 2) NOT NULL
);

-- Dados de Exemplo (Simulando histórico real)
INSERT INTO descontos_realizados (fornecedor, varejista, data_operacao, valor_desconto) VALUES
    ('Coca Cola', 'Grupo Pão de Açúcar', '2025-10-01', 500.00),  -- Coca -> Pão de Açúcar
    ('Nestlé Brasil', 'Carrefour', '2025-10-02', 1250.50), -- Nestlé -> Carrefour
    ('M Dias Branco', 'Açaí Atacadista', '2025-10-03', 300.00),  -- M Dias -> Açaí
    ('Coca Cola', 'Dia', '2025-10-04', 100.00);  -- Coca -> Dia
-- ============================================================
-- 3. TABELA DE DESCONTOS CALCULADOS
-- (O que a IA ou as Regras de Negócio dizem que deveria ser)
-- ============================================================
CREATE TABLE descontos_calculados (
    id SERIAL PRIMARY KEY,
    fornecedor TEXT NOT NULL REFERENCES organization_mappings(variavel),
    varejista TEXT NOT NULL REFERENCES organization_mappings(variavel),
    data_calculo DATE NOT NULL, -- Pode ser a mesma data da operação ou data do processamento
    valor_calculado DECIMAL(10, 2) NOT NULL
);

-- Dados de Exemplo (Simulando divergências para você testar)
INSERT INTO descontos_calculados (fornecedor, varejista, data_calculo, valor_calculado) VALUES
    -- Caso 1: Valor igual (Sem divergência)
    ('Coca Cola', 'Grupo Pão de Açúcar', '2025-10-01', 500.00),

    -- Caso 2: Divergência! Realizado foi 1250.50, mas calculado era 1500.00
    ('Nestlé Brasil', 'Carrefour', '2025-10-02', 1500.00), 

    -- Caso 3: Divergência! Realizado foi 300.00, calculado era 300.00 (Ok)
    ('M Dias Branco', 'Açaí Atacadista', '2025-10-03', 300.00);

-- ============================================================
-- 4. VIEW DE AUDITORIA (OPCIONAL)
-- Uma "tabela virtual" para ver os nomes reais cruzando os dados
-- ============================================================
-- ============================================================
-- 0. LIMPEZA
-- ============================================================
DROP VIEW IF EXISTS vw_auditoria_descontos;
DROP TABLE IF EXISTS descontos_calculados;
DROP TABLE IF EXISTS descontos_realizados;
DROP TABLE IF EXISTS organization_mappings;

-- ============================================================
-- 1. TABELA DE MAPEAMENTO
-- ============================================================
CREATE TABLE organization_mappings (
    id SERIAL PRIMARY KEY,
    organizacao TEXT NOT NULL UNIQUE,  -- Referência Principal agora
    variavel TEXT NOT NULL UNIQUE
);

INSERT INTO organization_mappings (organizacao, variavel) VALUES
    ('Coca Cola', 'FORNECEDOR_1'),
    ('Nestlé Brasil', 'FORNECEDOR_2'),
    ('M Dias Branco', 'FORNECEDOR_3'),
    ('Vivo', 'FORNECEDOR_4'),
    ('Grupo Pão de Açúcar', 'VAREJISTA_1'),
    ('Carrefour', 'VAREJISTA_2'),
    ('Açaí Atacadista', 'VAREJISTA_3'),
    ('Dia', 'VAREJISTA_4');

-- ============================================================
-- 2. TABELA DE DESCONTOS REALIZADOS
-- (Agora salvando NOMES REAIS)
-- ============================================================
CREATE TABLE descontos_realizados (
    id SERIAL PRIMARY KEY,
    -- A FK aponta para o NOME (organizacao), garantindo que a empresa exista
    fornecedor TEXT NOT NULL REFERENCES organization_mappings(organizacao),
    varejista TEXT NOT NULL REFERENCES organization_mappings(organizacao),
    data_operacao DATE NOT NULL,
    valor_desconto DECIMAL(10, 2) NOT NULL
);

INSERT INTO descontos_realizados (fornecedor, varejista, data_operacao, valor_desconto) VALUES
    ('Coca Cola', 'Grupo Pão de Açúcar', '2025-10-01', 500.00),
    ('Nestlé Brasil', 'Carrefour', '2025-10-02', 1250.50),
    ('M Dias Branco', 'Açaí Atacadista', '2025-10-03', 300.00),
    ('Coca Cola', 'Dia', '2025-10-04', 100.00);

-- ============================================================
-- 3. TABELA DE DESCONTOS CALCULADOS
-- (Agora salvando NOMES REAIS)
-- ============================================================
CREATE TABLE descontos_calculados (
    id SERIAL PRIMARY KEY,
    fornecedor TEXT NOT NULL REFERENCES organization_mappings(organizacao),
    varejista TEXT NOT NULL REFERENCES organization_mappings(organizacao),
    data_calculo DATE NOT NULL,
    valor_calculado DECIMAL(10, 2) NOT NULL
);

INSERT INTO descontos_calculados (fornecedor, varejista, data_calculo, valor_calculado) VALUES
    ('Coca Cola', 'Grupo Pão de Açúcar', '2025-10-01', 500.00),
    ('Nestlé Brasil', 'Carrefour', '2025-10-02', 1500.00), -- Divergência
    ('M Dias Branco', 'Açaí Atacadista', '2025-10-03', 300.00);

-- ============================================================
-- 4. VIEW DE AUDITORIA (Invertida)
-- Agora ela serve para buscar o TOKEN correspondente ao nome real
-- ============================================================
CREATE VIEW vw_auditoria_descontos AS
SELECT 
    r.id AS id_operacao,
    r.data_operacao,
    
    -- Dados Reais (Já estão na tabela)
    r.fornecedor AS nome_fornecedor,
    r.varejista AS nome_varejista,
    
    -- Buscamos o TOKEN (via Join) para o MCP usar se precisar
    org_f.variavel AS token_fornecedor,
    org_v.variavel AS token_varejista,
    
    -- Valores e Status
    r.valor_desconto AS valor_real,
    COALESCE(c.valor_calculado, 0) AS valor_ideal,
    (r.valor_desconto - COALESCE(c.valor_calculado, 0)) AS diferenca,
    
    CASE 
        WHEN c.valor_calculado IS NULL THEN 'NÃO CALCULADO'
        WHEN r.valor_desconto = c.valor_calculado THEN 'OK'
        ELSE 'DIVERGÊNCIA'
    END AS status

FROM descontos_realizados r
-- Join agora é feito pelo NOME para descobrir o TOKEN
JOIN organization_mappings org_f ON r.fornecedor = org_f.organizacao
JOIN organization_mappings org_v ON r.varejista = org_v.organizacao
LEFT JOIN descontos_calculados c ON 
    r.fornecedor = c.fornecedor AND 
    r.varejista = c.varejista AND 
    r.data_operacao = c.data_calculo;