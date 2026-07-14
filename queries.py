"""
queries.py
==========
All SQL query definitions for the dvdrental exercises (Exercise 1–14).

Structure
---------
queries         dict[str, str]
    Exercise 1–11 — plain SELECT statements, executed directly.

special_queries dict[str, dict[str, str]]
    Exercise 12 — view             (create or replace → select)
    Exercise 13 — materialized view (drop → create → select)
    Exercise 14 — temporary table  (create → select)

Each entry in special_queries must contain:
    "type"   : one of "temp_table" | "view" | "materialized_view"
    "create" : DDL statement
    "select" : SELECT statement to fetch results
    "drop"   : (materialized_view only) DROP statement run before CREATE
"""

from __future__ import annotations

# ──────────────────────────────────────────────────────────────────────────────
# Exercise 1–11  –  Standard SELECT queries (no DDL required)
# ──────────────────────────────────────────────────────────────────────────────
queries: dict[str, str] = {

    # ── Exercise 1 ── Film titles with daily rental price ─────────────────────
    "Exercise 1": """
        SELECT
        title AS "Film Title",
        rental_rate AS "Daily Price"
        FROM film
        ORDER BY title asc
        LIMIT 5;

    """,

    # ── Exercise 2 ── Films starting with 'A' between 60 and 120 minutes ──────
    "Exercise 2": """
        select title ,length from 
        film where title like 'A%'
        and length between 60 and 120
        order by length asc;
    """,

    # ── Exercise 3 ── Film count grouped by rating ────────────────────────────
    "Exercise 3": """
        select rating , count(rating) as "film_count"
        from film
        group by film.rating 
        order by film_count desc;

    """,

    # ── Exercise 4 ── Categories with more than 65 films ─────────────────────
    "Exercise 4": """
        select name as category, count(film_id) as film_count
        from category 
        join film_category 
        on category.category_id = film_category.category_id
        group by name
        having count(film_id)>65
        order by film_count desc;
    """,

    # ── Exercise 5 ── Each film with its category name ────────────────────────
    "Exercise 5": """
        select f.title , c.name as category
        from film as f
        inner join film_category as fc
        on f.film_id = fc.film_id 
        inner join category as c
        on fc.category_id  = c.category_id  
        order by c.name ,f.title ;
    """,

    # ── Exercise 6 ── Customer full name and email domain ─────────────────────
    "Exercise 6": """
        select upper(concat (first_name ,' ' ,last_name)) as customer_name , 
        SPLIT_PART(email, '@', 2) as email_domain
        from customer ;
    """,

    # ── Exercise 7 ── Combined list of all actors and staff (UNION) ───────────
    "Exercise 7": """
        select actor.first_name , actor.last_name  , 'actor' as type
        from actor
        union
        select staff.first_name , staff.last_name  , 'staff' as type
        from staff
        order by first_name , last_name ;

    """,

    # ── Exercise 8 ── Film count bucketed by length (short / medium / long) ───
    "Exercise 8": """
        select 
        case
            when length<60 then 'short'
            when length between 60 and 120 then 'medium'
            when length>120 then 'long'
        end as length_bucket,
        count(*) as films
        from film
        group by
        case
            when length<60 then 'short'
            when length between 60 and 120 then 'medium'
            when length>120 then 'long'
        end;
    """,

    # ── Exercise 9 ── Customers whose total spend is above the average ─────────
    "Exercise 9": """
       with customer_spending as(
        select  concat(c.first_name ,' ',c.last_name) as customer_name , SUM(p.amount) as total
        from customer as c
        inner join payment as p 
        on  c.customer_id = p.customer_id 
        group by 
        c.customer_id , c.first_name , C.last_name 
    ),
    avg_spending as (
        select avg(total) as avg_spent
        from customer_spending 
    )
    select customer_name , total 
    from customer_spending 
    where total >(
        select avg_spent from avg_spending 
    )
    order by total desc
    """,

    # ── Exercise 10 ── Films priced above the average rental rate ─────────────
    "Exercise 10": """
     select  title ,rental_rate 
    from film
    where rental_rate>(
    select AVG(rental_rate) as avg_rate 
    from film) 
    order by rental_rate desc;
    """,

    # ── Exercise 11 ── Films ranked by rentals within each category (RANK) ────
    "Exercise 11": """
     SELECT
    c.name AS category,
    f.title,
    COUNT(r.rental_id) AS rentals,
    RANK() OVER (
        PARTITION BY c.category_id
        ORDER BY COUNT(r.rental_id) DESC
    ) AS rnk
    FROM film f
    JOIN film_category fc
        ON f.film_id = fc.film_id
    JOIN category c
        ON fc.category_id = c.category_id
    JOIN inventory i
        ON f.film_id = i.film_id
    JOIN rental r
        ON i.inventory_id = r.inventory_id
    GROUP BY
        c.category_id,
        c.name,
        f.film_id,
        f.title;
    """,

}

# ──────────────────────────────────────────────────────────────────────────────
# Exercise 12–14  –  Special objects (view, materialized view, temp table)
# ──────────────────────────────────────────────────────────────────────────────
special_queries: dict[str, dict[str, str]] = {

    # ── Exercise 12 ── View: film catalog with category, rate & length ─────────
    "Exercise 12": {
        "type": "view",
        "create": """
            create or replace view film_catalog as
            select f.title, c.name as category,f.rental_rate,f.length
            from film as f
            join film_category as fc 
            on f.film_id = fc.film_id
            join category as c 
            on fc.category_id = c.category_id;
        """,
        "select": """
           SELECT
                title,
                rental_rate,
                length
            FROM film_catalog
            WHERE category = 'Comedy'
            ORDER BY title;
        """,
    },

    # ── Exercise 13 ── Materialized view: total revenue by category ───────────
    "Exercise 13": {
        "type": "materialized_view",
        "drop": "DROP MATERIALIZED VIEW IF EXISTS category_revenue;",
        "create": """
            CREATE MATERIALIZED VIEW category_revenue as
            select sum(p.amount) as revenue , c.name as category
            from payment as p 
            join rental as r 
            on p.rental_id = r.rental_id 
            join inventory as i
            on r.inventory_id = i.inventory_id
            join film_category as fc
            on i.film_id = fc.film_id
            join category as c
            on c.category_id = fc. category_id
            group by category;
        """,
        "select": """
            select category,revenue  
            from category_revenue 
            order by revenue desc 
            limit 5;

        """,
    },

    # ── Exercise 14 ── Temporary table: top 10 most rented films ─────────────
    "Exercise 14": {
        "type": "temp_table",
        "create": """
            create temporary table temp_rent as
            select f.title  , count(r.rental_id) as rentals
            from film as f
            join inventory as i 
            on f.film_id = i.film_id
            join rental as r 
            on i.inventory_id = r.inventory_id
            group by f.title
            order by rentals desc
            limit 10

        """,
        "select": """
          select * from temp_rent;
        """,
    },
}
