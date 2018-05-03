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

SET SERVEROUTPUT ON
-- nincs kész
--idő utáni
DECLARE
  days NUMBER;
  tmp_point NUMBER;
  CURSOR videok IS (SELECT MANAGER_VIDEO.TITLE, COUNT(*) FROM MANAGER_VIDEO, MANAGER_WATCHED
  WHERE MANAGER_VIDEO.ID = MANAGER_WATCHED.VIDEO_ID_ID AND MANAGER_VIDEO.CREATE_DATETIME
  GROUP BY MANAGER_VIDEO.TITLE ORDER BY);
BEGIN
    FOR vidi IN videok
        LOOP
            DBMS_OUTPUT.PUT_LINE('Pontok: ' || vidi.title);
        END LOOP;
END;
/



