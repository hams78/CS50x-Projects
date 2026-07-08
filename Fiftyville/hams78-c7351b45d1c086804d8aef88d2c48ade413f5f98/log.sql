-- Keep a log of any SQL queries you execute as you solve the mystery.

-- 1. Check crime scene report
SELECT description FROM crime_scene_reports WHERE year = 2025 AND month = 7 AND day = 28 AND street = 'Humphrey Street';

-- 2. Check interviews
SELECT name, transcript FROM interviews WHERE year = 2025 AND month = 7 AND day = 28 AND transcript LIKE '%bakery%';

-- 3. Find the thief
SELECT name FROM people
WHERE license_plate IN (
    SELECT license_plate FROM bakery_security_logs
    WHERE year = 2025 AND month = 7 AND day = 28 AND hour = 10 AND minute BETWEEN 15 AND 25 AND activity = 'exit'
)
AND id IN (
    SELECT person_id FROM bank_accounts
    WHERE account_number IN (
        SELECT account_number FROM atm_transactions
        WHERE year = 2025 AND month = 7 AND day = 28 AND atm_location = 'Leggett Street' AND transaction_type = 'withdraw'
    )
)
AND phone_number IN (
    SELECT caller FROM phone_calls
    WHERE year = 2025 AND month = 7 AND day = 28 AND duration < 60
)
AND passport_number IN (
    SELECT passport_number FROM passengers
    WHERE flight_id = (
        SELECT id FROM flights
        WHERE year = 2025 AND month = 7 AND day = 29 AND origin_airport_id = (SELECT id FROM airports WHERE city = 'Fiftyville')
        ORDER BY hour, minute LIMIT 1
    )
);

-- 4. Find the escape city
SELECT city FROM airports WHERE id = (
    SELECT destination_airport_id FROM flights
    WHERE year = 2025 AND month = 7 AND day = 29 AND origin_airport_id = (SELECT id FROM airports WHERE city = 'Fiftyville')
    ORDER BY hour, minute LIMIT 1
);

-- 5. Find the accomplice
SELECT name FROM people WHERE phone_number = (
    SELECT receiver FROM phone_calls
    WHERE caller = (SELECT phone_number FROM people WHERE name = 'Bruce')
    AND year = 2025 AND month = 7 AND day = 28 AND duration < 60
);
