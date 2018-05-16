SET SERVEROUTPUT ON

--legaktivabb tag
DECLARE
  max_point NUMBER;
  tmp_point NUMBER;
  other_tmp NUMBER;
  max_user AUTH_USER.USERNAME%TYPE;
  CURSOR userek IS (SELECT * FROM AUTH_USER);
  user_id AUTH_USER.ID%TYPE;
BEGIN
    max_point := 0;
    FOR m_rek IN userek
        LOOP
            SELECT COUNT(*) INTO other_tmp FROM MANAGER_VIDEO WHERE USER_ID = m_rek.ID;
            other_tmp := other_tmp * 5;
            SELECT COUNT(*) INTO tmp_point FROM MANAGER_COMMENT WHERE USER_ID = m_rek.ID;
            tmp_point := tmp_point * 2;
            tmp_point := tmp_point + other_tmp;

            IF tmp_point >= max_point THEN
                max_point := tmp_point;
                max_user := m_rek.username;
            END IF;

        END LOOP;
    DBMS_OUTPUT.PUT_LINE('Pontok: ' || max_point || ' User: ' || max_user);

END;
/

--videó keresés ahol X napnál nem régebbi és tartalamazza Y szöveget
SET SERVEROUTPUT ON
DECLARE
    CURSOR videok IS (
        SELECT MANAGER_VIDEO.ID, MANAGER_VIDEO.TITLE FROM MANAGER_VIDEO
        WHERE MANAGER_VIDEO.CREATE_DATETIME >= TRUNC(SYSDATE) - 30
        );
BEGIN
    FOR vidi IN videok LOOP
        IF vidi.TITLE LIKE '%haircut%' THEN

            DBMS_OUTPUT.PUT_LINE(vidi.ID || '__  TITLE: ' || vidi.TITLE);
        END IF;
    END LOOP;
END;
/

--Hasonló videók ajánlása
--A kategóriák kigyűjtése
-- backend majd leszámolja a leggyakoribbakat
SELECT MANAGER_VIDEO.ID, MANAGER_CATEGORY.NAME FROM MANAGER_VIDEO, MANAGER_VIDEOKATEGORIA, MANAGER_CATEGORY, MANAGER_WATCHED
WHERE
    MANAGER_VIDEO.ID = MANAGER_VIDEOKATEGORIA.VIDEO_ID_ID
    AND MANAGER_VIDEOKATEGORIA.KAT_ID_ID = MANAGER_CATEGORY.ID
    AND MANAGER_VIDEO.ID = MANAGER_WATCHED.VIDEO_ID_ID
    AND MANAGER_WATCHED.USER_ID = 2
ORDER BY MANAGER_WATCHED.WATCHED_DATE DESC
;

-- felvetődhet a kérdés miért nem kell group by -> többször is megnézhetett egy videót ekkor ennek nagyobb súlya lesz

-- Vissza adja a leghasonlóbb kategóriába tartozó videókat, amiket még nem látott a USER
SELECT MANAGER_VIDEO.TITLE FROM MANAGER_VIDEO, MANAGER_WATCHED, MANAGER_VIDEOKATEGORIA, MANAGER_CATEGORY
WHERE
    MANAGER_VIDEO.ID = MANAGER_VIDEOKATEGORIA.VIDEO_ID_ID
    AND MANAGER_VIDEOKATEGORIA.KAT_ID_ID = MANAGER_CATEGORY.ID
    AND MANAGER_VIDEO.ID = MANAGER_WATCHED.VIDEO_ID_ID
    AND MANAGER_WATCHED.USER_ID != 2
    AND MANAGER_CATEGORY.NAME IN ('Zucc','Aliens', 'Funny')
GROUP BY MANAGER_VIDEO.TITLE
;

--Az aktuális videó feltöltőjének egyéb videói
SELECT * FROM MANAGER_VIDEO WHERE USER_ID = 2 AND MANAGER_VIDEO.ID not LIKE "stringkód"