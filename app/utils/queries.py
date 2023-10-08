def insert_records_query(table_name, columns, placeholders):
    return f"""INSERT IGNORE INTO {table_name} ({columns}) VALUES ({placeholders});"""


def return_query_1(year: int):
    return f"""SELECT
                    d.department,
                    j.job,
                    SUM(CASE WHEN QUARTER(e.datetime) = 1 THEN 1 ELSE 0 END) AS Q1,
                    SUM(CASE WHEN QUARTER(e.datetime) = 2 THEN 1 ELSE 0 END) AS Q2,
                    SUM(CASE WHEN QUARTER(e.datetime) = 3 THEN 1 ELSE 0 END) AS Q3,
                    SUM(CASE WHEN QUARTER(e.datetime) = 4 THEN 1 ELSE 0 END) AS Q4
                FROM employees AS e
                LEFT JOIN departments AS d ON d.id = e.department_id
                LEFT JOIN jobs AS j ON j.id = e.job_id
                WHERE e.datetime BETWEEN '{year}-01-01' AND '{year}-12-31'
                GROUP BY d.department, j.job
                ORDER BY d.department ASC, j.job ASC;"""


def return_query_2(year: int):
    return f"""
                        SELECT
                            d.id AS department_id,
                            d.department AS department_name,
                            COUNT(*) AS num_employees_hired
                        FROM
                            employees e
                        INNER JOIN
                            departments d ON e.department_id = d.id
                        WHERE
                            e.datetime >= '{year}-01-01' AND e.datetime <= '{year}-12-31'
                        GROUP BY
                            d.id, d.department
                        HAVING
                            COUNT(*) > (
                                SELECT
                                    AVG(num_employees_hired)
                                FROM (
                                    SELECT
                                        d.id AS department_id,
                                        COUNT(*) AS num_employees_hired
                                    FROM
                                        employees e
                                    INNER JOIN
                                        departments d ON e.department_id = d.id
                                    WHERE
                                        e.datetime >= '{year}-01-01' AND e.datetime <= '{year}-12-31'
                                    GROUP BY
                                        d.id
                                ) AS subquery
                            )
                        ORDER BY
                            num_employees_hired DESC;"""
