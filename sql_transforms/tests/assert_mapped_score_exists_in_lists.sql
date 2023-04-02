-- `stg_lists` contain mapped score from the initial loading ("correct" anichan_score)
-- make sure these correct score still exist or is mapped correctly
WITH
check_winuyi_mapped_scores AS (
	SELECT DISTINCT anichan_score
	FROM stg_lists
	WHERE username = 'winuyi'
),

check_hammz_mapped_scores AS (
	SELECT DISTINCT anichan_score
	FROM stg_lists
	WHERE username = 'hammz'
)

SELECT 1
WHERE
	(40 NOT IN check_winuyi_mapped_scores)
	OR
	(60 NOT IN check_winuyi_mapped_scores)
	OR
	(80 NOT IN check_winuyi_mapped_scores)
	OR
	(100 NOT IN check_winuyi_mapped_scores)

UNION ALL

SELECT 1
WHERE
	(15 NOT IN check_hammz_mapped_scores)
	OR
	(20 NOT IN check_hammz_mapped_scores)
	OR
	(29 NOT IN check_hammz_mapped_scores)
	OR
	(31 NOT IN check_hammz_mapped_scores)
	OR
	(40 NOT IN check_hammz_mapped_scores)
	OR
	(60 NOT IN check_hammz_mapped_scores)
	OR
	(65 NOT IN check_hammz_mapped_scores)
	OR
	(71 NOT IN check_hammz_mapped_scores)
	OR
	(75 NOT IN check_hammz_mapped_scores)
	OR
	(76 NOT IN check_hammz_mapped_scores)
	OR
	(79 NOT IN check_hammz_mapped_scores)
	OR
	(80 NOT IN check_hammz_mapped_scores)
	OR
	(83 NOT IN check_hammz_mapped_scores)
	OR
	(84 NOT IN check_hammz_mapped_scores)
	OR
	(85 NOT IN check_hammz_mapped_scores)
	OR
	(86 NOT IN check_hammz_mapped_scores)
	OR
	(87 NOT IN check_hammz_mapped_scores)
	OR
	(88 NOT IN check_hammz_mapped_scores)
	OR
	(89 NOT IN check_hammz_mapped_scores)
	OR
	(91 NOT IN check_hammz_mapped_scores)
	OR
	(93 NOT IN check_hammz_mapped_scores)
	OR
	(94 NOT IN check_hammz_mapped_scores)
	OR
	(95 NOT IN check_hammz_mapped_scores)
	OR
	(96 NOT IN check_hammz_mapped_scores)
	OR
	(97 NOT IN check_hammz_mapped_scores)
	OR
	(99 NOT IN check_hammz_mapped_scores)
	OR
	(100 NOT IN check_hammz_mapped_scores)