# 20 Easy GrowALanguage Machine Problems With Programs

These are simplified machine problems for easier defense simulation. Each program still uses:

- `pollinate` function
- loop using `cultivate` or `grow`
- condition using `spring`, `bud`, or `wither`

The programs use small fixed values, so they are easier to trace by hand.

---

## Machine Problem 1: Even and Odd Counter

**Problem:** Count how many numbers from 1 to 5 are even and odd.

**Easy simulation:** `1, 3, 5` are odd. `2, 4` are even.

```gal
pollinate branch isEven(seed n) {
    spring (n % 2 == 0) {
        reclaim sunshine;
    }
    reclaim frost;
}

root() {
    seed even = 0;
    seed odd = 0;

    cultivate (seed i = 1; i <= 5; i++) {
        spring (isEven(i)) {
            even++;
        } wither {
            odd++;
        }
    }

    plant("Even: ", even);
    plant("Odd: ", odd);
    reclaim;
}
```

---

## Machine Problem 2: Sum from 1 to 5

**Problem:** Add numbers from 1 to 5 using a helper function.

**Easy simulation:** `1 + 2 + 3 + 4 + 5 = 15`.

```gal
pollinate seed add(seed a, seed b) {
    reclaim a + b;
}

root() {
    seed sum = 0;

    cultivate (seed i = 1; i <= 5; i++) {
        sum = add(sum, i);
    }

    spring (sum > 10) {
        plant("Big sum: ", sum);
    } wither {
        plant("Small sum: ", sum);
    }

    reclaim;
}
```

---

## Machine Problem 3: Countdown

**Problem:** Count down from 3 until the value becomes 0.

**Easy simulation:** Prints `3`, `2`, `1`, then `Done`.

```gal
pollinate branch stillCounting(seed n) {
    spring (n > 0) {
        reclaim sunshine;
    }
    reclaim frost;
}

root() {
    seed n = 3;

    grow (stillCounting(n)) {
        plant(n);
        n--;
    }

    plant("Done");
    reclaim;
}
```

---

## Machine Problem 4: Multiply by 2

**Problem:** Multiply 2 by numbers 1 to 5 and print products greater than 5.

**Easy simulation:** Products are `2, 4, 6, 8, 10`, so only `6, 8, 10` are printed.

```gal
pollinate seed multiply(seed a, seed b) {
    reclaim a * b;
}

root() {
    seed product = 0;

    cultivate (seed i = 1; i <= 5; i++) {
        product = multiply(2, i);
        spring (product > 5) {
            plant("Product: ", product);
        }
    }

    reclaim;
}
```

---

## Machine Problem 5: Pass or Fail

**Problem:** Check three fixed scores and print if each one passed or failed.

**Easy simulation:** Scores are `90`, `70`, and `80`.

```gal
pollinate branch isPassed(seed score) {
    spring (score >= 75) {
        reclaim sunshine;
    }
    reclaim frost;
}

root() {
    seed score = 0;

    cultivate (seed i = 1; i <= 3; i++) {
        spring (i == 1) {
            score = 90;
        } bud (i == 2) {
            score = 70;
        } wither {
            score = 80;
        }

        spring (isPassed(score)) {
            plant("Pass: ", score);
        } wither {
            plant("Fail: ", score);
        }
    }

    reclaim;
}
```

---

## Machine Problem 6: Factorial of 4

**Problem:** Compute the factorial of 4.

**Easy simulation:** `1 * 2 * 3 * 4 = 24`.

```gal
pollinate seed multiply(seed a, seed b) {
    reclaim a * b;
}

root() {
    seed result = 1;

    cultivate (seed i = 1; i <= 4; i++) {
        result = multiply(result, i);
    }

    plant("Factorial: ", result);
    reclaim;
}
```

---

## Machine Problem 7: Login on Second Try

**Problem:** Simulate a login where the correct PIN is entered on the second attempt.

**Easy simulation:** Attempt 1 uses `1111`, attempt 2 uses `1234`.

```gal
pollinate branch correct(seed pin) {
    spring (pin == 1234) {
        reclaim sunshine;
    }
    reclaim frost;
}

root() {
    seed attempt = 1;
    seed pin = 0;
    branch ok = frost;

    grow (attempt <= 3 && ok == frost) {
        spring (attempt == 2) {
            pin = 1234;
        } wither {
            pin = 1111;
        }

        spring (correct(pin)) {
            ok = sunshine;
        } wither {
            attempt++;
        }
    }

    spring (ok) {
        plant("Login success");
    } wither {
        plant("Locked");
    }

    reclaim;
}
```

---

## Machine Problem 8: Largest Number

**Problem:** Find the largest value from four fixed numbers.

**Easy simulation:** Numbers are `4`, `9`, `2`, and `7`. Largest is `9`.

```gal
pollinate seed bigger(seed a, seed b) {
    spring (a > b) {
        reclaim a;
    }
    reclaim b;
}

root() {
    seed current = 0;
    seed largest = 0;

    cultivate (seed i = 1; i <= 4; i++) {
        spring (i == 1) {
            current = 4;
        } bud (i == 2) {
            current = 9;
        } bud (i == 3) {
            current = 2;
        } wither {
            current = 7;
        }

        largest = bigger(largest, current);
    }

    plant("Largest: ", largest);
    reclaim;
}
```

---

## Machine Problem 9: Simple Bank Balance

**Problem:** Start with 100, deposit 50, withdraw 30, then try to withdraw 200.

**Easy simulation:** Balance becomes `150`, then `120`, then stays `120`.

```gal
pollinate seed deposit(seed balance, seed amount) {
    reclaim balance + amount;
}

pollinate seed withdraw(seed balance, seed amount) {
    spring (amount <= balance) {
        reclaim balance - amount;
    }
    reclaim balance;
}

root() {
    seed balance = 100;

    cultivate (seed step = 1; step <= 3; step++) {
        spring (step == 1) {
            balance = deposit(balance, 50);
        } bud (step == 2) {
            balance = withdraw(balance, 30);
        } wither {
            balance = withdraw(balance, 200);
        }
    }

    plant("Balance: ", balance);
    reclaim;
}
```

---

## Machine Problem 10: Find Number 3

**Problem:** Check numbers from 1 to 5 and print when number 3 is found.

**Easy simulation:** Only `i = 3` prints `Found`.

```gal
pollinate branch isTarget(seed n) {
    spring (n == 3) {
        reclaim sunshine;
    }
    reclaim frost;
}

root() {
    cultivate (seed i = 1; i <= 5; i++) {
        spring (isTarget(i)) {
            plant("Found: ", i);
        } wither {
            plant("Checked: ", i);
        }
    }

    reclaim;
}
```

---

## Machine Problem 11: Square Checker

**Problem:** Square numbers from 1 to 4 and classify each square as small or large.

**Easy simulation:** Squares are `1`, `4`, `9`, and `16`.

```gal
pollinate seed square(seed n) {
    reclaim n * n;
}

root() {
    seed value = 0;

    cultivate (seed i = 1; i <= 4; i++) {
        value = square(i);
        spring (value >= 9) {
            plant("Large square: ", value);
        } wither {
            plant("Small square: ", value);
        }
    }

    reclaim;
}
```

---

## Machine Problem 12: Count Numbers Greater Than 3

**Problem:** Count how many numbers from 1 to 6 are greater than 3.

**Easy simulation:** Numbers greater than 3 are `4`, `5`, and `6`.

```gal
pollinate branch gtThree(seed n) {
    spring (n > 3) {
        reclaim sunshine;
    }
    reclaim frost;
}

root() {
    seed count = 0;

    cultivate (seed i = 1; i <= 6; i++) {
        spring (gtThree(i)) {
            count++;
        }
    }

    plant("Count: ", count);
    reclaim;
}
```

---

## Machine Problem 13: Simple Discount

**Problem:** Add three item prices and apply a discount if the total reaches 100.

**Easy simulation:** Total is `30 + 40 + 50 = 120`, then discount makes it `110`.

```gal
pollinate seed applyDiscount(seed total) {
    spring (total >= 100) {
        reclaim total - 10;
    }
    reclaim total;
}

root() {
    seed total = 0;
    seed finalTotal = 0;

    cultivate (seed step = 1; step <= 3; step++) {
        spring (step == 1) {
            total += 30;
        } bud (step == 2) {
            total += 40;
        } wither {
            total += 50;
        }
    }

    finalTotal = applyDiscount(total);
    plant("Final total: ", finalTotal);
    reclaim;
}
```

---

## Machine Problem 14: Age Checker

**Problem:** Check three ages and print whether each age is minor or adult.

**Easy simulation:** Ages are `12`, `18`, and `25`.

```gal
pollinate branch isAdult(seed age) {
    spring (age >= 18) {
        reclaim sunshine;
    }
    reclaim frost;
}

root() {
    seed age = 0;

    cultivate (seed i = 1; i <= 3; i++) {
        spring (i == 1) {
            age = 12;
        } bud (i == 2) {
            age = 18;
        } wither {
            age = 25;
        }

        spring (isAdult(age)) {
            plant("Adult: ", age);
        } wither {
            plant("Minor: ", age);
        }
    }

    reclaim;
}
```

---

## Machine Problem 15: Times Three Table

**Problem:** Multiply numbers 1 to 4 by 3 and check if the product is odd or even.

**Easy simulation:** Products are `3`, `6`, `9`, and `12`.

```gal
pollinate seed timesThree(seed n) {
    reclaim n * 3;
}

root() {
    seed value = 0;

    cultivate (seed i = 1; i <= 4; i++) {
        value = timesThree(i);
        spring (value % 2 == 0) {
            plant("Even product: ", value);
        } wither {
            plant("Odd product: ", value);
        }
    }

    reclaim;
}
```

---

## Machine Problem 16: Hot Temperature Counter

**Problem:** Count how many temperatures are hot.

**Easy simulation:** Temperatures are `20`, `30`, and `35`. Hot means at least `30`.

```gal
pollinate branch isHot(seed temp) {
    spring (temp >= 30) {
        reclaim sunshine;
    }
    reclaim frost;
}

root() {
    seed temp = 0;
    seed hot = 0;

    cultivate (seed i = 1; i <= 3; i++) {
        spring (i == 1) {
            temp = 20;
        } bud (i == 2) {
            temp = 30;
        } wither {
            temp = 35;
        }

        spring (isHot(temp)) {
            hot++;
        }
    }

    plant("Hot days: ", hot);
    reclaim;
}
```

---

## Machine Problem 17: Smallest Number

**Problem:** Find the smallest value from four fixed numbers.

**Easy simulation:** Numbers are `8`, `3`, `6`, and `10`. Smallest is `3`.

```gal
pollinate seed smaller(seed a, seed b) {
    spring (a < b) {
        reclaim a;
    }
    reclaim b;
}

root() {
    seed current = 0;
    seed smallest = 99;

    cultivate (seed i = 1; i <= 4; i++) {
        spring (i == 1) {
            current = 8;
        } bud (i == 2) {
            current = 3;
        } bud (i == 3) {
            current = 6;
        } wither {
            current = 10;
        }

        smallest = smaller(smallest, current);
    }

    spring (smallest < 5) {
        plant("Very small: ", smallest);
    } wither {
        plant("Smallest: ", smallest);
    }

    reclaim;
}
```

---

## Machine Problem 18: Fibonacci First Five

**Problem:** Print the first five Fibonacci numbers.

**Easy simulation:** Output sequence is `0`, `1`, `1`, `2`, `3`.

```gal
pollinate seed nextFib(seed a, seed b) {
    reclaim a + b;
}

root() {
    seed a = 0;
    seed b = 1;
    seed next = 0;

    plant(a);
    plant(b);

    cultivate (seed i = 3; i <= 5; i++) {
        next = nextFib(a, b);
        plant(next);
        a = b;
        b = next;
    }

    spring (b >= 3) {
        plant("End: ", b);
    }

    reclaim;
}
```

---

## Machine Problem 19: Simple Point Game

**Problem:** Add one point every odd-numbered round from rounds 1 to 5.

**Easy simulation:** Points are added on rounds `1`, `3`, and `5`, so score is `3`.

```gal
pollinate seed addPoint(seed score) {
    reclaim score + 1;
}

root() {
    seed score = 0;

    cultivate (seed round = 1; round <= 5; round++) {
        spring (round % 2 == 1) {
            score = addPoint(score);
        }
    }

    spring (score >= 3) {
        plant("Win: ", score);
    } wither {
        plant("Lose: ", score);
    }

    reclaim;
}
```

---

## Machine Problem 20: Find First Multiple of 4

**Problem:** Find the first number from 1 to 10 that is divisible by 4.

**Easy simulation:** The first multiple of 4 is `4`.

```gal
pollinate branch isMultipleFour(seed n) {
    spring (n % 4 == 0) {
        reclaim sunshine;
    }
    reclaim frost;
}

root() {
    seed i = 1;
    seed found = 0;

    grow (i <= 10 && found == 0) {
        spring (isMultipleFour(i)) {
            found = i;
        } wither {
            i++;
        }
    }

    plant("First multiple of 4: ", found);
    reclaim;
}
```
