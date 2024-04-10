WITH RECURSIVE Ancestors AS (
  SELECT i.ind_id, i.pere_id, i.mere_id, 1 AS generation
  FROM individu AS i
  WHERE i.ind_id = 72

  UNION ALL

  SELECT c.ind_id, c.pere_id, c.mere_id, a.generation + 1
  FROM individu AS c
  JOIN Ancestors AS a ON (c.ind_id = a.pere_id OR c.ind_id = a.mere_id)
),
AncestorsIds AS (SELECT ind_id FROM Ancestors)

SELECT i.ind_id, i.nom, i.prenom, d.doc_id, d.doc_type, i.date_n, i.commune_n_text, i.date_d, i.commune_d_text, d.chemin
FROM 
	AncestorsIds natural join Individu as i
	natural join document_individu_assoc 
	natural join document as d
;