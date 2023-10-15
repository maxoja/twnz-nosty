SELECT
  users.id,
  SUM(charges.amountGbp) as amountGbp,
  MAX(charges.created) as lastCreated,
  MAX(charges.updated) lastUpdated
FROM
  charges
  JOIN
    users ON charges.users LIKE '%' || users.id || '%'
GROUP BY
  users.id;
