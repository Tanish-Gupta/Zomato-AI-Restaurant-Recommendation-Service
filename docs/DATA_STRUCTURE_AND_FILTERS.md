# Data Structure and Filter Comparison

This document describes the dataset columns and how API inputs are compared when filtering restaurants.

---

## Column mapping (API → dataset)

After loading and preprocessing, the repository maps logical names to actual column names:

| API / logical name | Dataset column |
|--------------------|----------------|
| `name`             | `name` |
| `cuisine`          | `cuisines` |
| `location`         | `location` |
| `rating`           | `rate` |
| `price`            | `approx_cost(for_two_people)` |
| `votes`            | `votes` |

---

## All columns (after preprocessing)

```
url, address, name, online_order, book_table, rate, votes, phone, location,
rest_type, dish_liked, cuisines, approx_cost(for_two_people), reviews_list,
menu_item, listed_in(type), listed_in(city)
```

---

## 1. Cuisine

- **Dataset column:** `cuisines`
- **Type:** String (often comma-separated, e.g. `"Chinese, North Indian, Thai"`)
- **Comparison:** Substring match (case-insensitive)  
  `df['cuisines'].str.lower().str.contains(your_input.lower(), na=False)`
- **Example values:**  
  `Chinese, Mughlai, North Indian` · `Cafe, Italian, Mexican` · `North Indian` · `American, Burger, Fast Food` · …
- **Total unique cuisine strings:** ~1,919 (combinations)
- **UI input:** Single choice from dropdown (e.g. "American", "North Indian"). A row matches if that text appears anywhere in the `cuisines` string.

---

## 2. Location

- **Dataset column:** `location`
- **Type:** String
- **Comparison:** Substring match (case-insensitive)  
  `df['location'].str.lower().str.contains(your_input.lower(), na=False)`
- **Example values:**  
  Banashankari, Basavanagudi, Jayanagar, Jp Nagar, Koramangala, Indiranagar, Whitefield, Kengeri, …
- **Total unique locations:** 94
- **UI input:** Single choice from dropdown. A row matches if the location string contains the selected value.

---

## 3. Rating (min_rating)

- **Dataset column:** `rate`
- **Type:** Float (0–5) after preprocessing. Original values like `"4.1/5"` are parsed to `4.1`.
- **Comparison:**  
  Keep row if **rating is missing (NaN)** OR **numeric rating ≥ min_rating**  
  `(rating_series.isna()) | (rating_series >= min_rating)`
- **Value range in data:** Min ~1.8, Max ~4.9. Many rows have NaN (unrated).
- **UI input:** Optional number 0–5. `0` is treated as “no minimum” (no rating filter).

---

## 4. Price range

- **Dataset column:** `approx_cost(for_two_people)`
- **Type in data:** String (e.g. `"800"`, `"300"`, `"1,200"`) — rupee cost for two people.
- **Category column:** `approx_cost(for_two_people)_category` is **not** created in this dataset, because the preprocessor only adds `_category` for **numeric** price columns. Here the column stays string.
- **Comparison when category exists:**  
  `df[price_col + '_category'].str.lower() == price_range.lower()`  
  (exact match: `low` | `medium` | `high` | `very_high`.)
- **Fallback when no category:**  
  `df[col].astype(str).str.lower().str.contains(price_range.lower(), na=False)`  
  So the code looks for the substring `"low"`, `"medium"`, `"high"`, or `"very_high"` inside the cost string (e.g. `"800"`). **None of the cost strings contain those words**, so filtering by price range currently returns no rows.
- **Preprocessor price mapping (when column is numeric):**  
  `1 → "low"`, `2 → "medium"`, `3 → "high"`, `4 → "very_high"`. Any other number defaults to `"medium"`.
- **UI input:** One of `Any` | `low` | `medium` | `high` | `very_high`. With current data, only “Any” yields results when other filters are used.

---

## 5. Sample row (one restaurant)

| Field    | Example value |
|----------|-------------------------------|
| name     | Jalsa |
| cuisines | Chinese, Mughlai, North Indian |
| location | Banashankari |
| rate     | 4.1 |
| approx_cost(for_two_people) | 800 |

---

## Summary

- **Cuisine** and **location** work by **substring** match on `cuisines` and `location`.
- **Rating** works by **numeric** comparison on `rate` (with NaN treated as “no rating” so they are not excluded by min_rating).
- **Price range** does **not** work as intended with the current dataset: the cost column is string (rupee values), no `_category` column is created, and the fallback comparison does not match any row. To support price filtering, the pipeline would need to map rupee ranges to `low`/`medium`/`high`/`very_high` and store that in a category column (or equivalent).
