-- ¿Cuántas personas hay en cada posición?
SELECT * FROM v_resumen_posiciones;

-- ¿Cuáles son las habilidades más altas de cada posición? (promedios de 1 a 5)
SELECT posicion, "Regate", "Definición", "Defensa", "Reflejos", "Juego aéreo" FROM v_perfil_habilidades_sql;

-- ¿Qué modelo tuvo mejores resultados?
SELECT * FROM v_modelos_ordenados;

-- ¿Qué extremos se calificaron con regate 5? (une dos tablas: valor limpio y respuesta original)
SELECT p.id_persona, p.edad, p.regate, o.regate AS regate_original FROM participantes p JOIN respuestas_originales o ON o.id_persona = p.id_persona WHERE p.posicion = 'Extremo' AND p.regate = 5 ORDER BY p.id_persona LIMIT 8;

-- ¿Cuántos casos marcados hay y de qué tipo?
SELECT SUM(duplicado_posible) AS duplicados_posibles, SUM(duplicado_repetida) AS duplicados_repetidos, SUM(menor_18) AS menores_18, SUM(edad_atipica) AS edades_atipicas, SUM(linea_recta) AS linea_recta, SUM(incoherencia_experiencia) AS incoherencias FROM participantes;

