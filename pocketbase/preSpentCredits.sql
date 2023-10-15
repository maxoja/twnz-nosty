SELECT
  users.id,
  users.username,
  SUM(topups.amountGbp) as amountGbp,
  MAX(topups.updated) as updated
FROM
  users
  JOIN
    topups ON users.id = topups.user
GROUP BY
  users.id, users.username;