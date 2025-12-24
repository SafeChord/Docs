# 測試設計與流程

## 目的

本測試設計旨在驗證疫情數據系統的正確性，涵蓋數據生成、聚合檢查與比例計算三個主要方面。雖然我們使用 IO 工具與 SQL 指令來協助驗證過程，但實際的結果驗證將採用手動檢查的方式，以確保每個場景的細節都能被仔細確認。

## 測試流程

1. **數據生成**：使用 `simulate` 指令生成測試期間的病例數據。
2. **預期結果計算**：撰寫 SQL 指令，生成與測試場景匹配的預期結果。
3. **驗證**：使用 `verify` 指令執行測試，並將結果與 SQL 查詢進行對比。

## simulate 指令

用於生成測試期間的病例數據：

`szio simulate 2023-04-01`
`szio simulate 2023-04-02 --end-date=2023-04-30`

## verify 指令

用於檢查數據聚合結果與正確性，涵蓋以下場景：

### 邊界或異常場景

1. `szio verify 2023-03-01 --city=台北市`：測試空數據的情境。

### 國家級聚合

1. `szio verify 2023-04-01`
2. `szio verify 2023-04-07 --interval=7`

### 城市級聚合

1. `szio verify 2023-04-02 --city=台北市 --interval=3`

### 城市級比例

1. `szio verify 2023-04-25 --city=台北市 --ratio --interval=14`

### 地區級聚合

1. `szio verify 2023-04-25 --city=新北市 --region=板橋區 --interval=14`

### 地區級聚合

1. `szio verify 2023-04-25 --city=新北市 --region=板橋區 --interval=14`

### 地區級比例

1. `szio verify 2023-04-25 --city=新北市 --region=板橋區 --ratio --interval=30`

## 覆蓋場景檢查

- **日期範圍**：所有 `interval` 的值（1, 3, 7, 14, 30）都有涉及，符合需求。
- **地點粒度**：涵蓋了國家級、城市級（台北市）、地區級（新北市板橋區）。
- **數據模式**：
    - 聚合病例數（`aggregated_cases`）：所有 `verify` 指令默認檢查。
    - 比例檢查（`--ratio`）：在城市級和地區級場景中均有測試。
- **數據分佈邏輯**：覆蓋了多個組合情境，包括城市與區域的篩選、單日與範圍數據的檢查。

# 測試資料與 SQL 指令

## 國家病例數

### 指令: `szio verify 2023-04-01`

```sql
SELECT
    SUM(c.cases) AS aggregated_cases
FROM
    covid_cases c
WHERE
    c.date = '2023-04-01';

```

- [x]  測試通過

### 指令: `szio verify 2023-04-07 --interval=7`

```sql
SELECT
    SUM(c.cases) AS aggregated_cases
FROM
    covid_cases c
WHERE
    c.date BETWEEN '2023-04-01' AND '2023-04-07';

```

- [x]  測試通過

## 城市病例數

### 指令: `szio verify 2023-04-02 --city=台北市 --interval=3`

```sql
SELECT
    SUM(c.cases) AS aggregated_cases
FROM
    covid_cases c
JOIN
    cities ct ON c.city_id = ct.id
WHERE
    ct.name = '台北市'
    AND c.date BETWEEN '2023-03-31' AND '2023-04-02';

```

- [x]  測試通過

### 指令: `szio verify 2023-04-25 --city=台北市 --ratio --interval=14`

```sql
SELECT
    SUM(c.cases) * 10000.0 / (
    SELECT SUM(population)
    FROM populations p
    JOIN cities ct ON p.city_id = ct.id
    WHERE ct.name = '台北市'
) * 1.0 AS cases_population_ratio
FROM
    covid_cases c
JOIN
    cities ct ON c.city_id = ct.id
WHERE
    ct.name = '台北市'
    AND c.date BETWEEN '2023-04-12' AND '2023-04-25';

```

- [x]  測試通過

## 區域病例數

### 指令: `szio verify 2023-04-25 --city=新北市 --region=板橋區 --interval=14`

```sql
SELECT
    SUM(c.cases)
FROM
    covid_cases c
JOIN
    cities ct ON c.city_id = ct.id
JOIN
    regions r ON c.region_id = r.id
WHERE
    ct.name = '新北市'
    AND r.name = '板橋區'
    AND c.date BETWEEN '2023-04-12' AND '2023-04-25';

```

- [x]  測試通過

### 指令: `szio verify 2023-04-25 --city=新北市 --region=板橋區 --ratio --interval=30`

```sql
SELECT
    SUM(c.cases) * 10000.0  / (
    SELECT population
    FROM populations p
    JOIN cities ct ON p.city_id = ct.id
    JOIN regions r ON p.region_id = r.id
    WHERE ct.name = '新北市' AND r.name = '板橋區'
) * 1.0 AS cases_population_ratio
FROM
    covid_cases c
JOIN
    cities ct ON c.city_id = ct.id
JOIN
    regions r ON c.region_id = r.id
WHERE
    ct.name = '新北市'
    AND r.name = '板橋區'
    AND c.date BETWEEN '2023-03-26' AND '2023-04-25';

```

- [x]  測試通過

## 邊界或異常場景

### 指令: `szio verify 2023-03-01 --city=台北市`

```sql
SELECT
    SUM(c.cases) AS aggregated_cases
FROM
    covid_cases c
JOIN
    cities ct ON c.city_id = ct.id
WHERE
    ct.name = '台北市'
    AND c.date = '2023-03-01';

```

- [x]  測試通過