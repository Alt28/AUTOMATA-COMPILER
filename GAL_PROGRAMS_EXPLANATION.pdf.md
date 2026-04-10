# GAL Programs — Detailed Explanation Document

> **Author:** Clarence  
> **Language:** GAL (Garden Abstraction Language)  
> **Date Range:** March 7 – April 8, 2026  

---

## GAL Keyword Quick Reference

Before diving into the programs, here is a reference table of GAL keywords and their equivalents:

| GAL Keyword | Meaning | Equivalent |
|-------------|---------|------------|
| `seed` | Integer variable | `int` |
| `tree` | Float variable | `double` / `float` |
| `leaf` | Character variable | `char` |
| `vine` | String variable | `string` |
| `branch` | Boolean variable | `bool` |
| `sunshine` | True | `true` |
| `frost` | False | `false` |
| `fertile` | Constant | `const` |
| `plant()` | Print output | `printf` / `print` |
| `water()` | Read input | `scanf` / `input` |
| `spring()` | If statement | `if` |
| `bud()` | Else-if statement | `else if` |
| `wither` | Else statement | `else` |
| `grow()` | While loop | `while` |
| `cultivate()` | For loop | `for` |
| `tend` | Do-while loop | `do-while` |
| `harvest()` | Switch statement | `switch` |
| `variety` | Case in switch | `case` |
| `soil` | Default in switch | `default` |
| `prune` | Break | `break` |
| `pollinate` | Function declaration | `function` |
| `empty` | Void return type | `void` |
| `reclaim` | Return | `return` |
| `root()` | Main function | `main()` |
| `skip` | Continue statement | `continue` |
| `bundle` | Struct definition | `struct` |
| `~` | Negation sign | `-` (unary minus) |
| `` ` `` | String concatenation | `+` (for strings) |
| `**` | Exponentiation | `pow()` |
| `++` / `--` | Increment / Decrement | `x++` / `x--` |
| `+=`, `-=`, `*=`, `/=`, `%=` | Compound assignment | same as C |
| `(seed)x`, `(tree)x`, etc. | Type casting | `(int)x` in C |
| `.ts` | String/array length | `.length` |
| `.wilt` | String to lowercase | `.lower()` |
| `.bloom` | String to uppercase | `.upper()` |
| `word[i]` | Vine string indexing | `str[i]` |
| `.taper` | Array/string pop last | `.pop()` |
| `.append(...)` | Array append | `.push()` / `.append()` |
| `.insert(i, ...)` | Array insert at index | `.insert()` |
| `.remove(i)` | Array remove at index | `.splice()` / `.pop(i)` |

### Important Note on `plant()`

`plant()` does **NOT** auto-add newlines. It behaves like C's `printf()`. You must use `\n` explicitly for line breaks:
```
plant("Hello\n");                   ~~ prints "Hello" then moves to next line
plant("Value: {}\n", x);            ~~ prints value with newline
plant("* ");                         ~~ prints on SAME line (no newline)
plant("\n");                         ~~ just a newline
```

For printing patterns (triangles, tables), use `plant()` for same-line output and `plant("\n")` at the end of each row.

---

# MARCH 7 — Programs 1 to 4: Basic Arithmetic Operations

## What was asked?
Input 2 numbers and show: 1) sum, 2) difference, 3) product, 4) quotient.  
**Constraints:** No parameter passing, no function calling, no choices.

---

### Program 1: Sum

```
root() {
    seed a;
    seed b;
    seed sum;

    plant("Enter 1st number: ");
    water(a);
    plant("Enter 2nd number: ");
    water(b);

    sum = a + b;
    plant("Sum: ", sum);
    reclaim;
}
```

**Line-by-line explanation:**

1. `root()` — This is the main function. Every GAL program must have exactly one `root()`. It is where execution starts, like `main()` in C.

2. `seed a;` / `seed b;` / `seed sum;` — Declares three integer variables. `seed` means integer. We need two variables for the two input numbers and one to store the result.

3. `plant("Enter 1st number: ");` — Prints the prompt text to the screen. `plant()` is GAL's print function.

4. `water(a);` — Reads user input and stores it into variable `a`. `water()` is GAL's input function. This is the older syntax where you pass the variable directly.

5. `sum = a + b;` — Adds the two numbers and stores the result in `sum`.

6. `plant("Sum: ", sum);` — Prints the label "Sum: " followed by the value of `sum`.

7. `reclaim;` — Returns from `root()`. Every `root()` function MUST end with `reclaim ;` — this is a mandatory GAL rule.

**Why `seed` and not `tree`?** The problem says "integers", so `seed` (integer type) is appropriate. If we needed decimal results, we'd use `tree` (float type).

---

### Program 2: Difference

Identical structure to Program 1, but uses `diff = a - b;` instead of addition. The variable is named `diff` to clearly indicate what it stores.

### Program 3: Product

Same structure, uses `prod = a * b;`.

---

### Program 4: Quotient

```
root() {
    seed a;
    seed b;
    tree q;

    plant("Enter 1st number: ");
    water(a);
    plant("Enter 2nd number: ");
    water(b);

    grow (b == 0) {
        plant("Cannot divide by zero. Enter 2nd number again: ");
        water(b);
    }

    q = a / b;
    plant("Quotient: ", q);
    reclaim;
}
```

**Key differences from Programs 1-3:**

1. **`tree q;` instead of `seed q;`** — We use `tree` (float) because division often produces decimal results. For example, 7 / 2 = 3.5. If we used `seed`, the result would be truncated to 3.

2. **`grow (b == 0) { ... }`** — This is a `while` loop. It keeps executing as long as `b` equals 0.
   - **Why do we need this?** Division by zero is mathematically undefined and would cause a runtime error. This loop is a safety guard — it prevents the program from crashing.
   - **How does it work?** If the user enters 0 for `b`, the loop body runs: it prints an error message and asks for input again. The loop repeats until the user enters a non-zero value.
   - **Why `grow` (while) and not `spring` (if)?** With `spring` (if), if the user enters 0 a second time, the program would still crash. `grow` (while) keeps asking until a valid value is given.

---

# MARCH 7 — Program 5: Multiplication Table

## What was asked?
Input row and column to indicate the size of a multiplication table.

```
root() {
    seed rows;
    seed cols;
    seed i;
    seed j;
    seed prod;

    plant("Enter number of rows: ");
    water(rows);
    plant("Enter number of columns: ");
    water(cols);

    cultivate (i = 1; i <= rows; i++) {
        cultivate (j = 1; j <= cols; j++) {
            prod = i * j;

            spring (prod < 10) {
                plant("  ");
            } bud (prod < 100) {
                plant(" ");
            } wither {
                plant("");
            }
            plant(prod);
            plant(" ");
        }
        plant("\n");
    }

    reclaim;
}
```

**How it works:**

1. **Nested `cultivate` loops** — The outer loop (`i`) handles rows. The inner loop (`j`) handles columns. For each combination of `i` and `j`, we compute `prod = i * j`.

2. **The alignment logic (`spring`/`bud`/`wither`):**
   - `spring (prod < 10)` — If the product is a single digit (1-9), print 2 extra spaces before it.
   - `bud (prod < 100)` — If the product is two digits (10-99), print 1 extra space.
   - `wither` — If three digits (100+), no extra space needed.
   - **Why?** This right-aligns the numbers so the table looks clean and readable. Without padding, columns would be misaligned.

3. **`plant("\n");`** — After each complete row, print a newline character to move to the next line.

**Example output for rows=3, cols=4:**
```
  1   2   3   4
  2   4   6   8
  3   6   9  12
```

---

# MARCH 7 — Programs 6-9: Shape Patterns

## What was asked?
Input row count and use asterisks to display: 6) triangle, 7) inverted triangle, 8) rectangle, 9) square.

### Program 6: Triangle

```
cultivate (i = 1; i <= n; i++) {
    cultivate (j = 1; j <= i; j++) {
        plant("*");
    }
    plant("\n");
}
```

**How it works:**
- Row 1: inner loop runs `j = 1 to 1` → prints 1 star
- Row 2: inner loop runs `j = 1 to 2` → prints 2 stars
- Row 3: inner loop runs `j = 1 to 3` → prints 3 stars
- ...and so on

**The key is `j <= i`** — the inner loop's limit equals the current row number, so each row has one more star than the previous row.

**Output for n=4:**
```
*
**
***
****
```

### Program 7: Inverted Triangle

```
cultivate (i = n; i >= 1; i--) {
```

**Only difference:** The outer loop counts DOWN from `n` to 1 instead of UP. So row 1 prints `n` stars, row 2 prints `n-1`, etc.

**Output for n=4:**
```
****
***
**
*
```

### Program 8: Rectangle

```
cultivate (i = 1; i <= rows; i++) {
    cultivate (j = 1; j <= cols; j++) {
        plant("*");
    }
    plant("\n");
}
```

**Difference from triangle:** Inner loop always runs to `cols` (fixed width), not `i`. Every row has the same number of stars.

### Program 9: Square

Same as rectangle but `rows = cols = n`, so it's a square.

---

# MARCH 7 — Program 10: Fibonacci Sequence

## What was asked?
Input a number N and generate the first N Fibonacci numbers.

**What is Fibonacci?** Each number is the sum of the two before it: 0, 1, 1, 2, 3, 5, 8, 13, ...

```
root() {
    seed n;
    seed i;
    seed a = 0;
    seed b = 1;
    seed next;

    plant("Enter length of Fibonacci series: ");
    water(n);

    spring (n <= 0) {
        plant("Invalid length.");
        reclaim;
    }

    plant(a);
    spring (n >= 2) {
        plant(b);
    }

    cultivate (i = 3; i <= n; i++) {
        next = a + b;
        plant(next);
        a = b;
        b = next;
    }

    reclaim;
}
```

**Step by step:**

1. **`a = 0; b = 1;`** — The first two Fibonacci numbers are always 0 and 1.

2. **Edge cases:**
   - `n <= 0` → invalid, print error and exit immediately with `reclaim`.
   - `n == 1` → only print `a` (which is 0).
   - `n >= 2` → also print `b` (which is 1).

3. **The loop starts at `i = 3`** because we've already printed the first 2 numbers. For each iteration:
   - `next = a + b` — compute the next Fibonacci number
   - `a = b; b = next;` — shift the window forward

4. **Why not use recursion here?** This was a March 7 program — no functions were allowed yet. Also, recursive Fibonacci is extremely slow for large N (exponential time complexity), while iterative is O(N).

**Trace for n=6:**
```
Start: a=0, b=1 → print 0, 1
i=3: next = 0+1 = 1, print 1, a=1, b=1
i=4: next = 1+1 = 2, print 2, a=1, b=2
i=5: next = 1+2 = 3, print 3, a=2, b=3
i=6: next = 2+3 = 5, print 5, a=3, b=5
Output: 0 1 1 2 3 5
```

---

# MARCH 12 — Program 1: Square Root (Newton's Method)

## What was asked?
Compute the square root of a user input number.

```
pollinate tree sqrtApprox(tree n) {
    tree guess;
    tree nextGuess;
    tree diff;
    tree absDiff;

    guess = n / 2.0;
    nextGuess = 0.0;
    diff = 1.0;
    absDiff = 1.0;

    spring (n == 0.0) {
        reclaim 0.0;
    }

    grow (absDiff > 0.000001) {
        nextGuess = (guess + (n / guess)) / 2.0;
        diff = nextGuess - guess;
        spring (diff < 0.0) {
            absDiff = ~1 * diff;
        }
        wither {
            absDiff = diff;
        }
        guess = nextGuess;
    }

    reclaim guess;
}
```

**Concept: Newton's Method (Babylonian Method)**

This is a mathematical algorithm to approximate square roots. The idea is:
- Start with a guess (we use `n / 2`)
- Repeatedly improve the guess using the formula: `nextGuess = (guess + n/guess) / 2`
- Stop when the guess stops changing significantly

**Why does this formula work?**
- If `guess` is too high, then `n/guess` will be too low (and vice versa)
- Averaging them gives a better approximation
- Each iteration roughly doubles the number of correct digits

**Line-by-line:**

1. **`guess = n / 2.0`** — Initial guess. Half the number is a reasonable starting point.

2. **`spring (n == 0.0) { reclaim 0.0; }`** — Edge case: square root of 0 is 0. Without this, we'd divide by zero in the formula (`n / guess` where `guess = 0`).

3. **`grow (absDiff > 0.000001)`** — Keep iterating until the change between iterations is smaller than 0.000001 (our precision threshold). This gives us about 6 decimal places of accuracy.

4. **`absDiff = ~1 * diff;`** — GAL doesn't have a built-in `abs()` function. The `~` is GAL's negation operator. So `~1 * diff` is the same as `-1 * diff`, which flips a negative number to positive. This gives us the absolute value.

5. **Why `tree` everywhere?** Square roots are almost always decimal numbers (e.g., √2 = 1.41421...), so we need float types.

**Trace for n=16:**
```
guess = 8.0
Iteration 1: nextGuess = (8 + 16/8) / 2 = (8+2)/2 = 5.0
Iteration 2: nextGuess = (5 + 16/5) / 2 = (5+3.2)/2 = 4.1
Iteration 3: nextGuess = (4.1 + 16/4.1) / 2 ≈ 4.001
Iteration 4: nextGuess ≈ 4.00000006 → converged!
Result: 4.0
```

---

# MARCH 12 — Programs 2-3: Sum of Squares / Sum of Cubes

## What was asked?
Compute the sum of squares (or cubes) of numbers from 1 to N.

### Program 2: Sum of Squares

```
pollinate seed sumOfSquares(seed n) {
    seed i;
    seed total;
    total = 0;

    cultivate(i = 1; i <= n; i++) {
        total = total + (i * i);
    }

    reclaim total;
}
```

**How it works:**

1. **`pollinate seed sumOfSquares(seed n)`** — This declares a function named `sumOfSquares` that:
   - Returns a `seed` (integer)
   - Takes one parameter `n` of type `seed`
   - `pollinate` is the keyword for declaring functions (other than `root()`)

2. **`total = total + (i * i);`** — For each number from 1 to N, we square it (`i * i`) and add it to the running total.

3. **`reclaim total;`** — Returns the accumulated sum.

**For N=4:** 1² + 2² + 3² + 4² = 1 + 4 + 9 + 16 = **30**

### Program 3: Sum of Cubes

Identical but uses `total = total + (i * i * i);` — cubing instead of squaring.

**For N=3:** 1³ + 2³ + 3³ = 1 + 8 + 27 = **36**

**Why separate functions?** This follows good programming practice — the computation logic is isolated in a function, making the code reusable and testable. The `root()` function only handles input/output.

---

# MARCH 12 — Program 4a: Binary to Decimal/Octal/Hexadecimal

## What was asked?
Input a binary number, convert it to decimal, octal, and hexadecimal.

This is the most complex program so far. It uses **4 helper functions**.

### Function 1: `isBinary(seed n)` — Input Validation

```
pollinate branch isBinary(seed n) {
    seed temp;
    seed digit;
    temp = n;

    spring (temp == 0) {
        reclaim sunshine;
    }

    grow (temp > 0) {
        digit = temp % 10;
        spring ((digit != 0) && (digit != 1)) {
            reclaim frost;
        }
        temp = temp / 10;
    }

    reclaim sunshine;
}
```

**What it does:** Checks that every digit of the input number is either 0 or 1 (i.e., it's a valid binary number).

**How:**
- `temp % 10` extracts the last digit
- If that digit is anything other than 0 or 1, return `frost` (false)
- `temp / 10` removes the last digit
- Repeat until all digits are checked
- If we get through the whole number without finding an invalid digit, return `sunshine` (true)

**Why `branch` return type?** Because we're returning a true/false value. `branch` is GAL's boolean type.

### Function 2: `binaryToDecimal(seed n)` — Binary → Decimal Conversion

```
pollinate seed binaryToDecimal(seed n) {
    seed temp;
    seed digit;
    seed base;
    seed dec;
    temp = n;
    base = 1;
    dec = 0;

    grow (temp > 0) {
        digit = temp % 10;
        dec = dec + (digit * base);
        base = base * 2;
        temp = temp / 10;
    }

    reclaim dec;
}
```

**How binary-to-decimal conversion works:**

Binary numbers use powers of 2. Each digit position has a value:
- Rightmost digit: 2⁰ = 1
- Next: 2¹ = 2
- Next: 2² = 4
- And so on...

**Process:**
1. Extract the rightmost digit (`temp % 10`)
2. Multiply it by the current power of 2 (`base`)
3. Add to the decimal result
4. Double the base (`base * 2`) for the next position
5. Remove the processed digit (`temp / 10`)

**Trace for binary 1101:**
```
digit=1, base=1: dec = 0 + (1×1) = 1
digit=0, base=2: dec = 1 + (0×2) = 1
digit=1, base=4: dec = 1 + (1×4) = 5
digit=1, base=8: dec = 5 + (1×8) = 13
Result: 13
```

### Function 3: `printOctal(seed n)` — Decimal → Octal (Recursive)

```
pollinate empty printOctal(seed n) {
    seed q;
    seed r;
    q = n / 8;
    r = n % 8;

    spring (n > 7) {
        printOctal(q);
    }

    plant(r);
    reclaim;
}
```

**Key concept: Recursion for digit ordering**

To convert decimal to octal, we repeatedly divide by 8 and collect remainders. But the remainders come out in **reverse order**. Recursion solves this elegantly:
1. Recurse FIRST (to handle the higher-order digits)
2. Print AFTER the recursive call returns

**Why not just use a loop?** A loop would give us digits in reverse order (least significant first). We'd need a string or array to reverse them. Recursion naturally gives us the correct order because it "unwinds" from the deepest call first.

**Trace for n=13:**
```
printOctal(13): q=1, r=5. Since 13>7, call printOctal(1)
  printOctal(1): q=0, r=1. Since 1≤7, don't recurse. Print 1.
Back to printOctal(13): Print 5.
Output: 15 (which is 13 in octal ✓)
```

### Function 4: `hexDigit(seed n)` and `printHex(seed n)`

`hexDigit` maps numbers 10-15 to letters A-F using a `spring/bud/wither` chain (like a switch statement). `printHex` uses the same recursive technique as `printOctal` but divides by 16 instead of 8.

---

# MARCH 12 — Program 4b: Decimal to Binary/Octal/Hexadecimal

## What was asked?
Input a decimal number (can have a fractional part) and convert to binary, octal, and hexadecimal.

This program handles both **whole parts** and **fractional parts** separately.

### Whole Part Conversion: `toBinWhl(seed n)`

```
pollinate vine toBinWhl(seed n) {
    vine result;
    seed q;
    seed r;
    result = "";
    q = n / 2;
    r = n % 2;

    spring (q > 0) {
        result = toBinWhl(q);
    }
    result = result ` (vine) r;
    reclaim result;
}
```

**How it differs from `printOctal`:** Instead of printing directly, this function **builds a string**. The `` ` `` operator concatenates strings, and `(vine) r` casts the integer remainder to a string.

**Why return a string?** Because the caller needs to assemble the full output: `"Binary: " + wholePart + "." + fractionalPart`. You can't do this if the function just prints directly.

### Fractional Part Conversion: `toBinFrac(tree frac, seed limit)`

```
pollinate vine toBinFrac(tree frac, seed limit) {
    vine result;
    seed i;
    seed digit;
    result = "";

    cultivate(i = 0; i < limit; i++) {
        frac = frac * 2.0;
        digit = frac;
        result = result ` (vine) digit;
        frac = frac - digit;
    }

    reclaim result;
}
```

**How fractional binary conversion works:**
1. Multiply the fraction by 2
2. The integer part of the result is the next binary digit
3. Keep only the fractional part
4. Repeat up to `limit` times (we use 6 digits of precision)

**Trace for 0.75:**
```
frac=0.75 × 2 = 1.5 → digit=1, frac=0.5
frac=0.5 × 2 = 1.0 → digit=1, frac=0.0
Result: "11" → 0.75 in binary is 0.11 ✓
```

**Why `limit = 6`?** Some fractions (like 0.1) have infinite binary representations. We limit to 6 digits to prevent infinite loops.

---

# MARCH 12 — Program 5: Reverse of Digits

### 5a: Sum of Digits

```
pollinate seed sumDigits(seed n) {
    seed temp;
    seed digit;
    seed total;
    temp = n;
    total = 0;

    grow (temp > 0) {
        digit = temp % 10;
        total = total + digit;
        temp = temp / 10;
    }

    reclaim total;
}
```

**The "digit extraction" pattern** — used in many programs throughout:
- `temp % 10` → gives the LAST digit (e.g., 156 % 10 = 6)
- `temp / 10` → removes the last digit (e.g., 156 / 10 = 15, integer division)

This pattern loops until `temp` becomes 0, processing one digit per iteration.

**Trace for 156:**
```
temp=156: digit = 156%10 = 6, total = 0+6 = 6, temp = 156/10 = 15
temp=15:  digit = 15%10 = 5,  total = 6+5 = 11, temp = 15/10 = 1
temp=1:   digit = 1%10 = 1,   total = 11+1 = 12, temp = 1/10 = 0
Result: 12 ✓
```

### 5b: Reverse Digits

```
grow (temp > 0) {
    digit = temp % 10;
    rev = (rev * 10) + digit;
    temp = temp / 10;
}
```

**The "reverse number" pattern:**
- `rev * 10` shifts the current reversed number left by one position
- `+ digit` places the extracted digit in the ones position

**Trace for 156:**
```
temp=156: digit=6, rev = 0×10 + 6 = 6,   temp=15
temp=15:  digit=5, rev = 6×10 + 5 = 65,  temp=1
temp=1:   digit=1, rev = 65×10 + 1 = 651, temp=0
Result: 651 ✓
```

---

# MARCH 16 — Program 1: Area Calculator (Switch Statement)

## What was asked?
Calculate area of Circle, Triangle, Square, or Rectangle using switch statement.

```
root() {
    plant("Area Calculator") ;
    plant("1 - Circle") ;
    plant("2 - Triangle") ;
    plant("3 - Square") ;
    plant("4 - Rectangle") ;
    plant("Enter choice: ") ;
    seed choice = water() ;

    harvest(choice) {
        variety 1:
            plant("Enter radius: ") ;
            tree r = water() ;
            tree aCircle = 3.14159 * r * r ;
            plant("Area of Circle: {}", aCircle) ;
            prune ;
        variety 2:
            plant("Enter base: ") ;
            tree b = water() ;
            plant("Enter height: ") ;
            tree h = water() ;
            tree aTriangle = 0.5 * b * h ;
            plant("Area of Triangle: {}", aTriangle) ;
            prune ;
        variety 3:
            plant("Enter side: ") ;
            tree s = water() ;
            tree aSquare = s * s ;
            plant("Area of Square: {}", aSquare) ;
            prune ;
        variety 4:
            plant("Enter length: ") ;
            tree l = water() ;
            plant("Enter width: ") ;
            tree w = water() ;
            tree aRect = l * w ;
            plant("Area of Rectangle: {}", aRect) ;
            prune ;
        soil:
            plant("Invalid Input") ;
            prune ;
    }
    reclaim ;
}
```

**Key concepts:**

1. **`harvest(choice)`** = switch statement. It evaluates `choice` and jumps to the matching `variety`.

2. **`variety 1:`** = case 1. Each variety block handles one shape.

3. **`prune ;`** = break. Without this, execution would "fall through" to the next variety (just like C's switch without break).

4. **`soil:`** = default case. Catches any choice that isn't 1-4.

5. **`plant("Area of Circle: {}", aCircle)`** — The `{}` is a placeholder that gets replaced by the value of `aCircle`. This is GAL's format string syntax.

6. **Why unique variable names (`aCircle`, `aTriangle`, `aSquare`, `aRect`)?**  
   In GAL, all `variety` blocks share the same function scope. If you declared `tree area` in variety 1, then tried to declare `tree area` again in variety 2, you'd get a "Variable already declared" error. Each case needs its own unique variable name.

7. **Area formulas used:**
   - Circle: A = π × r² (`3.14159 * r * r`)
   - Triangle: A = ½ × b × h (`0.5 * b * h`)
   - Square: A = s² (`s * s`)
   - Rectangle: A = l × w (`l * w`)

---

# MARCH 16 — Program 2: Area Calculator (Sub-Functions)

## What was asked?
Same as Program 1, but each calculation is done in a sub-function with parameter passing.

```
pollinate tree calcCircle(tree r) {
    reclaim (3.14159 * r * r) ;
}

pollinate tree calcTriangle(tree b, tree h) {
    reclaim (0.5 * b * h) ;
}

pollinate tree calcSquare(tree s) {
    reclaim (s * s) ;
}

pollinate tree calcRect(tree l, tree w) {
    reclaim (l * w) ;
}
```

**Why use sub-functions?**
- **Separation of concerns:** Input/output is in `root()`, computation is in functions.
- **Reusability:** You could call `calcCircle()` from anywhere, multiple times.
- **Testability:** Each function can be tested independently.
- **Readability:** The main function is cleaner.

**How parameter passing works:**
1. `root()` reads the input values (e.g., `tree r = water()`)
2. Passes them to the function: `area = calcCircle(r)`
3. The function receives the value in its parameter, computes, and returns the result
4. `root()` receives the return value and prints it

**Key difference:** Now we CAN use a shared `tree area = 0.0` variable because we're storing the RETURN VALUE, not declaring new variables in each case.

---

# MARCH 16 — Programs 3A/3B: Print Natural Numbers Recursively

## What was asked?
A: Print first 50 natural numbers using recursion.
B: Print first N natural numbers (user input) using recursion.

```
pollinate empty printNums(seed n, seed max) {
    spring(n > max) {
        reclaim ;
    }
    plant("{} ", n) ;
    printNums(n + 1, max) ;
    reclaim ;
}
```

**Understanding recursion through this example:**

**What is recursion?** A function that calls itself. Every recursive function needs:
1. **Base case** — when to STOP (prevents infinite recursion)
2. **Recursive case** — the function calls itself with a "smaller" problem

**In this program:**
- **Base case:** `spring(n > max) { reclaim ; }` — when `n` exceeds `max`, stop.
- **Recursive case:** `printNums(n + 1, max)` — call itself with `n` incremented by 1.

**Why `pollinate empty`?** The function doesn't return a value — it just prints. `empty` is GAL's void type.

**Why TWO `reclaim ;` statements?** 
- The first `reclaim ;` (inside the `spring` block) exits when the base case is reached.
- The second `reclaim ;` (at the end) is mandatory — every function in GAL must end with `reclaim ;`.

**Trace for printNums(1, 3):**
```
printNums(1, 3): 1 > 3? No. Print "1 ". Call printNums(2, 3).
  printNums(2, 3): 2 > 3? No. Print "2 ". Call printNums(3, 3).
    printNums(3, 3): 3 > 3? No. Print "3 ". Call printNums(4, 3).
      printNums(4, 3): 4 > 3? Yes! Return.
    Return.
  Return.
Return.
Output: "1 2 3 "
```

---

# MARCH 16 — Program 4: Array Print + Sort (Recursion)

## What was asked?
A: Print array elements using recursion.
B: Sort array ascending or descending (user choice).

This is the most complex program so far. It uses the **array parameter passing** feature (`seed arr[]`).

### `printArr` — Recursive Array Printing

```
pollinate empty printArr(seed arr[], seed n, seed i) {
    spring(i >= n) {
        reclaim ;
    }
    plant("{} ", arr[i]) ;
    printArr(arr, n, i + 1) ;
    reclaim ;
}
```

**How it works:** Same pattern as `printNums`, but instead of printing `n`, it prints `arr[i]` — the element at index `i`. The array `arr[]` is passed by reference, meaning the function accesses the SAME array, not a copy.

### `bblPass` — One Pass of Bubble Sort (Recursive)

```
pollinate empty bblPass(seed arr[], seed n, seed i) {
    spring(i >= n - 1) {
        reclaim ;
    }
    spring(arr[i] > arr[i + 1]) {
        seed temp = arr[i] ;
        arr[i] = arr[i + 1] ;
        arr[i + 1] = temp ;
    }
    bblPass(arr, n, i + 1) ;
    reclaim ;
}
```

**What is Bubble Sort?**
Bubble sort works by repeatedly comparing adjacent elements and swapping them if they're in the wrong order. After one complete pass, the largest element "bubbles up" to the end.

**How this recursive version works:**
1. **Base case:** `i >= n - 1` — we've compared all adjacent pairs in this pass.
2. **Swap logic:** If `arr[i] > arr[i + 1]`, swap them using a temporary variable:
   - `temp = arr[i]` — save the first value
   - `arr[i] = arr[i + 1]` — overwrite first with second
   - `arr[i + 1] = temp` — put saved value in second position
3. **Recurse:** Move to the next pair (`i + 1`).

### `sortAsc` — Full Bubble Sort (Recursive)

```
pollinate empty sortAsc(seed arr[], seed n) {
    spring(n <= 1) {
        reclaim ;
    }
    bblPass(arr, n, 0) ;
    sortAsc(arr, n - 1) ;
    reclaim ;
}
```

**How it works:**
1. Do one complete pass (`bblPass`), which puts the largest element at position `n-1`.
2. Recurse with `n - 1` — now we only need to sort the first `n-1` elements (the last one is already in place).
3. **Base case:** `n <= 1` — an array of 0 or 1 elements is already sorted.

**Trace for [64, 34, 25]:**
```
sortAsc(arr, 3):
  bblPass(arr, 3, 0): compare (64,34)→swap→[34,64,25], compare (64,25)→swap→[34,25,64]
  sortAsc(arr, 2):
    bblPass(arr, 2, 0): compare (34,25)→swap→[25,34,64]
    sortAsc(arr, 1): base case, return.
Result: [25, 34, 64] ✓
```

### Descending Sort

`bblPassDsc` uses `arr[i] < arr[i + 1]` instead of `>` — swaps when the left element is SMALLER, pushing small elements to the end.

---

# MARCH 16 — Program 5: Count Digits Recursion

```
pollinate seed countDig(seed n) {
    spring(n < 10) {
        reclaim 1 ;
    }
    reclaim 1 + countDig(n / 10) ;
}
```

**How it works:**
- **Base case:** `n < 10` means it's a single digit → return 1.
- **Recursive case:** Count 1 for the current rightmost digit, then recurse on `n / 10` (which removes the rightmost digit).

**Trace for n=50:**
```
countDig(50): 50 < 10? No. Return 1 + countDig(50/10) = 1 + countDig(5)
  countDig(5): 5 < 10? Yes. Return 1.
Back: 1 + 1 = 2
Result: 2 ✓
```

---

# MARCH 23 — Program 1: Sum of Positives Until 0

```
root() {
    seed num;
    seed sum = 0;

    plant("Enter integers (enter 0 to stop):\n");
    plant("Number: ");
    num = water();

    grow (num != 0) {
        spring (num > 0) {
            sum = sum + num;
        }
        plant("Number: ");
        num = water();
    }

    plant("\nSum of all positive integers: {}\n", sum);
    reclaim;
}
```

**Key design decisions:**

1. **Sentinel value pattern:** The loop continues until a specific value (0) is entered. 0 is the "sentinel" — it signals the user is done.

2. **The first `water()` is BEFORE the loop** — This is called a "priming read." Without it, the loop condition `num != 0` would check an uninitialized variable on the first iteration.

3. **`spring (num > 0)`** — Only adds positive numbers to the sum. Negative numbers are ignored (not added, not treated as stop signal).

4. **Why `grow` and not `cultivate`?** We don't know in advance how many numbers the user will enter. `grow` (while) checks a condition, `cultivate` (for) is for known iteration counts.

---

# MARCH 23 — Program 2: Duplicate Detection

```
grow (found == frost) {
    plant("Number: ");
    num = water();

    i = 0;
    grow (i < count) {
        spring (nums[i] == num) {
            found = sunshine;
        }
        i = i + 1;
    }

    spring (found == sunshine) {
        plant("\nDuplicate found: {}\n", num);
    }
    bud (found == frost) {
        nums[count] = num;
        count = count + 1;
    }
}
```

**Algorithm: Linear Search**

1. Read a new number
2. Compare it against ALL previously stored numbers (`nums[0]` to `nums[count-1]`)
3. If a match is found, set `found = sunshine` and report the duplicate
4. If no match, store the number and increment `count`
5. Repeat until a duplicate is found

**Why `seed nums[100]`?** We need to store all entered numbers. 100 is the maximum capacity — a safe upper limit. We track actual count with `count`.

---

# MARCH 23 — Program 3: Factorial (While Loop)

```
i = num;
grow (i > 1) {
    fact = fact * i;
    i = i - 1;
}
```

**What is factorial?** n! = n × (n-1) × (n-2) × ... × 2 × 1

**How:** Start at `num`, multiply into `fact`, decrement `i`. The loop stops when `i` reaches 1.

**Trace for num=5:**
```
fact=1, i=5: fact = 1×5 = 5,   i=4
fact=5, i=4: fact = 5×4 = 20,  i=3
fact=20, i=3: fact = 20×3 = 60, i=2
fact=60, i=2: fact = 60×2 = 120, i=1 → stop
Result: 120 ✓
```

**Why `fact = 1` initially?** Because 1 is the multiplicative identity — multiplying by 1 doesn't change the result. If we started with 0, everything would be 0.

---

# MARCH 23 — Program 4: Username Validation

```
grow (valid == frost) {
    plant("Enter a username (at least 8 characters): ");
    username = water();
    len = username.ts;

    spring (len >= 8) {
        valid = sunshine;
    }
    bud (len < 8) {
        plant("Invalid! Username is only {} characters. Try again.\n", len);
    }
}
```

**Key concept: `.ts` property**

`username.ts` returns the length of the string (number of characters). `.ts` is GAL's built-in string length property (think of it as "total size").

**Loop logic:** Keep asking until `valid` becomes `sunshine` (true). The `grow` loop checks `valid == frost` (false) — as soon as a valid username is entered, `valid` is set to `sunshine`, and the loop ends.

---

# MARCH 23 — Program 5.1: Number Palindrome

```
grow (num > 0) {
    remainder = num % 10;
    reversed = reversed * 10 + remainder;
    num = num / 10;
}

spring (original == reversed) {
    plant("{} is a palindrome.\n", original);
}
```

**What is a palindrome?** A number (or word) that reads the same forwards and backwards. E.g., 121, 1331, 12321.

**Algorithm:** Reverse the number and compare with the original. If they're equal, it's a palindrome.

**Why save `original = num`?** Because the reversal loop modifies `num` (divides it down to 0). We need the original value for comparison.

---

# MARCH 23 — Program 5.2: Word Palindrome

```
left = 0;
right = n - 1;
grow (left < right) {
    spring (letters[left] != letters[right]) {
        isPalin = frost;
    }
    left = left + 1;
    right = right - 1;
}
```

**Algorithm: Two-Pointer Technique**

1. Set `left` to the first index (0) and `right` to the last index (n-1)
2. Compare `letters[left]` with `letters[right]`
3. If they differ → not a palindrome
4. Move both pointers inward (`left++`, `right--`)
5. Repeat until they meet in the middle

**Why use `leaf letters[50]` array?** Although GAL now supports vine string indexing (`word[i]`), this program was originally written before that feature was added. You could alternatively use `vine` with indexing: `word[left] != word[right]`.

**Trace for "racecar" (r,a,c,e,c,a,r):**
```
left=0, right=6: r == r ✓
left=1, right=5: a == a ✓
left=2, right=4: c == c ✓
left=3, right=3: left < right is false → stop
isPalin = sunshine → "racecar is a palindrome" ✓
```

---

# MARCH 31 Set A — Program 1: Sort 5-Letter Word

```
spring (choice == 1) {
    cultivate(seed k = 97; k <= 122; k++) {
        spring (c1 == (leaf)k) { result = result ` (vine)(leaf)k; }
        spring (c2 == (leaf)k) { result = result ` (vine)(leaf)k; }
        spring (c3 == (leaf)k) { result = result ` (vine)(leaf)k; }
        spring (c4 == (leaf)k) { result = result ` (vine)(leaf)k; }
        spring (c5 == (leaf)k) { result = result ` (vine)(leaf)k; }
    }
    plant("\nAscending: {}\n", result);
}
```

**Algorithm: Counting Sort by ASCII value**

**Why ASCII 97-122?** These are the ASCII codes for lowercase letters: 'a'=97, 'b'=98, ..., 'z'=122.

**How it works:**
1. Loop through ALL possible characters from 'a' to 'z' (k = 97 to 122)
2. For each character, check if ANY of the 5 input characters matches `(leaf)k` (cast integer to char)
3. If it matches, append it to the result string

**Why this produces sorted output:** Because we iterate in alphabetical order (a→z), characters are naturally added in sorted sequence.

**Type casting chain:** `(vine)(leaf)k`
- `(leaf)k` — cast integer 97 to character 'a'
- `(vine)` — cast character 'a' to string "a" (needed for string concatenation with `` ` ``)

**For descending:** Same logic but loop from 122 down to 97 (`k--`).

---

# MARCH 31 Set A — Program 2: Array Addition

Straightforward: Three arrays A, B, C. Input A and B, compute `C[i] = A[i] + B[i]` for each index. Print all three.

# MARCH 31 Set A — Program 3: Student Grade Averages

Repeats the same input-and-average pattern for 4 subjects. Uses `(tree)sum / 5` to cast the integer sum to float before dividing, ensuring decimal precision.

# MARCH 31 Set A — Program 4: Even Sum + Odd Average

Uses `i % 2 == 0` to detect even numbers and `i % 2 != 0` for odd. The modulo operator `%` returns the remainder — even numbers have remainder 0 when divided by 2.

---

# MARCH 31 Set A — Program 5: GCD (Euclidean Algorithm)

```
pollinate seed gcd(seed a, seed b) {
    spring (b == 0) {
        reclaim a;
    }
    reclaim gcd(b, a % b);
}
```

**The Euclidean Algorithm** is one of the oldest algorithms in mathematics (over 2300 years old).

**Principle:** GCD(a, b) = GCD(b, a mod b). When b becomes 0, a is the GCD.

**Why it works:** The GCD of two numbers also divides their difference (and remainder). So we can keep reducing the problem until one number becomes 0.

**Trace for GCD(48, 18):**
```
gcd(48, 18): b≠0, return gcd(18, 48%18) = gcd(18, 12)
gcd(18, 12): b≠0, return gcd(12, 18%12) = gcd(12, 6)
gcd(12, 6):  b≠0, return gcd(6, 12%6)   = gcd(6, 0)
gcd(6, 0):   b=0, return 6
Result: 6 ✓ (48 = 6×8, 18 = 6×3)
```

---

# MARCH 31 Set B — Program 1: Largest Element (Recursion)

```
pollinate seed findLargest(seed max, seed count, seed n) {
    spring(count >= n) {
        reclaim max;
    }
    seed element = water();
    spring(element > max) {
        reclaim findLargest(element, count + 1, n);
    }
    reclaim findLargest(max, count + 1, n);
}
```

**Unique approach:** Instead of storing all elements in an array first, this function reads input DURING recursion.

**How:** Carries the current maximum (`max`) through recursive calls. Each call reads one element, compares it with `max`, and passes the larger value forward.

---

# MARCH 31 Set B — Program 2: LCM

Uses the mathematical relationship: **LCM(a,b) = (a × b) / GCD(a,b)**

This is efficient because we already have the GCD function. Computing LCM from scratch would require more complex logic.

---

# MARCH 31 Set B — Program 3: Hailstone (Collatz) Sequence

```
pollinate empty hailstone(seed n) {
    plant("{}", n);
    spring(n == 1) {
        reclaim;
    }
    spring(n % 2 == 0) {
        seed half = n / 2;
        hailstone((seed)half);
    }
    wither {
        hailstone(n * 3 + 1);
    }
    reclaim;
}
```

**The Collatz Conjecture:**
- If `n` is even: divide by 2
- If `n` is odd: multiply by 3 and add 1
- The conjecture states this sequence always reaches 1 (unproven but true for all tested numbers)

**Why `(seed)half`?** Explicit cast to ensure integer division result stays as `seed` type.

---

# MARCH 31 Set B — Programs 4-5: Capital Letter Detection

### `isUpper(vine ch)` — The Character Classifier

```
pollinate branch isUpper(vine ch) {
    spring(ch == "A" || ch == "B" || ch == "C" || ... || ch == "M") {
        reclaim sunshine;
    }
    bud(ch == "N" || ch == "O" || ... || ch == "Z") {
        reclaim sunshine;
    }
    reclaim frost;
}
```

**Why check against strings ("A") not characters ('A')?** The function takes `vine ch` (string parameter) because each character is read via `water()` which returns a string. Comparing string to string is required by GAL's type system.

**Why split into two conditions?** The `||` chain for all 26 letters was too long for one line, so it's split into A-M and N-Z across `spring` and `bud` blocks.

---

# APRIL 8 — Program 1: Strong Number

**Definition:** A strong number is one where the sum of the factorial of each digit equals the number itself.

**Example:** 145 → 1! + 4! + 5! = 1 + 24 + 120 = 145 ✓

```
pollinate seed sumDigitFact(seed n) {
    spring(n == 0) {
        reclaim 0;
    }
    seed digit = n % 10;
    seed rest = n / 10;
    reclaim factorial(digit) + sumDigitFact((seed)rest);
}
```

**How:** Recursively extracts each digit, computes its factorial, and sums them all up. Uses the same digit-extraction pattern (`% 10` and `/ 10`).

---

# APRIL 8 — Program 2: Perfect Number

**Definition:** A perfect number equals the sum of its proper divisors (all divisors except itself).

**Example:** 6 → divisors: 1, 2, 3 → sum = 6 ✓

```
pollinate seed sumDivisors(seed n, seed i) {
    spring(i == n) {
        reclaim (0) ;
    }
    spring(n % i == 0) {
        reclaim (i + sumDivisors(n, i + 1)) ;
    }
    wither {
        reclaim (sumDivisors(n, i + 1)) ;
    }
}
```

**How:** Recursively checks each number from 1 to n-1. If `i` divides `n` evenly (`n % i == 0`), it's a divisor — add it. Otherwise, skip it.

---

# APRIL 8 — Program 3: Prime Numbers in Range

```
pollinate seed isPrime(seed n, seed i) {
    spring(n <= 1) { reclaim (0) ; }
    spring(i == n) { reclaim (1) ; }
    spring(n % i == 0) { reclaim (0) ; }
    wither { reclaim (isPrime(n, i + 1)) ; }
}
```

**How `isPrime` works:**
1. Numbers ≤ 1 are NOT prime → return 0
2. If we've tested all divisors from 2 to n-1 without finding one (`i == n`) → it IS prime → return 1
3. If `i` divides `n` evenly → NOT prime → return 0
4. Otherwise, try the next divisor (`i + 1`)

**Why start at `i = 2`?** Every number is divisible by 1, so testing 1 is meaningless. We start at 2 (the smallest prime).

`printPrimes` walks through the range and prints only numbers where `isPrime` returns 1.

---

# APRIL 8 — Program 4: Digit Frequency

```
pollinate seed countDigit(seed n, seed d) {
    spring(n == 0) { reclaim (0) ; }
    tree div = n / 10 ;
    seed next = (seed)div ;
    spring(n % 10 == d) {
        reclaim (1 + countDigit(next, d)) ;
    }
    wither {
        reclaim (countDigit(next, d)) ;
    }
}
```

**How:** For each digit position of `n`, check if the digit (`n % 10`) equals the target digit `d`. If yes, count 1 + the count from the remaining digits. If no, just count the remaining digits.

`printFreq` calls `countDigit` for each digit 0-9 and prints only those with count > 0.

---

# APRIL 8 — Program 5: Automorphic Number

**Definition:** A number whose square ends with the number itself.

**Examples:** 5 → 5² = 25 (ends with 5) ✓ | 6 → 6² = 36 (ends with 6) ✓ | 76 → 76² = 5776 (ends with 76) ✓

**Formula:** n² mod 10^(number of digits in n) should equal n.

```
seed digits = numDigits(num) ;
seed mod = power(10, digits) ;
seed remainder = sq % mod ;
spring(remainder == num) { ... }
```

**How:** If `num = 76`, it has 2 digits, so `mod = 10² = 100`. Then `76² = 5776`, and `5776 % 100 = 76`, which equals `num`. Therefore 76 is automorphic.

---

# APRIL 8 — Program 6: Neon Number

**Definition:** A number where the sum of digits of its square equals the number itself.

**Example:** 9 → 9² = 81 → 8 + 1 = 9 ✓

Simple: compute square, sum its digits, compare with original.

---

# APRIL 8 — Program 7: Disarium Number

**Definition:** A number where the sum of each digit raised to the power of its position equals the number.

**Example:** 135 → 1¹ + 3² + 5³ = 1 + 9 + 125 = 135 ✓

```
pollinate seed disariumSum(seed n, seed pos) {
    spring(n == 0) { reclaim (0) ; }
    tree div = n / 10 ;
    seed next = (seed)div ;
    seed digit = n % 10 ;
    reclaim (disariumSum(next, pos - 1) + power(digit, pos)) ;
}
```

**How:** Processes digits from right to left. The rightmost digit is at position `pos` (which equals the total number of digits initially). Each recursive call reduces `pos` by 1 and removes the rightmost digit.

**Why `pos - 1` in the recursive call?** Because we're moving left through the number. The next digit to the left has position `pos - 1`.

---

# Summary of Programming Patterns Used

| Pattern | Where Used | How It Works |
|---------|-----------|--------------|
| Digit extraction | Programs 5a/b, Strong, Neon, Automorphic, Disarium, Digit Freq | `n % 10` gets last digit, `n / 10` removes it |
| Number reversal | Palindrome number | `rev = rev * 10 + digit` builds number backwards |
| Two-pointer | Palindrome word | Compare from both ends, move inward |
| Sentinel loop | Sum until 0 | Loop until special value entered |
| Recursive traversal | Natural numbers, array print | Process current element, recurse for rest |
| Recursive sort | Bubble sort | One pass + recurse with smaller array |
| Recursive accumulation | Sum of squares, digit count | Return current value + recursive result |
| Newton's method | Square root | Iteratively refine guess with formula |
| Euclidean algorithm | GCD | GCD(a,b) = GCD(b, a%b) |
| Counting sort | Letter sorting | Loop through all possible values in order |
| Divide and conquer | Number base conversion | Repeatedly divide by base, collect remainders |

---

# GAL COMPILER SPECIFICATION

The following sections document the internal compiler components: the Context-Free Grammar (CFG), FIRST/FOLLOW/PREDICT sets, operator precedence, semantic rules, AST node types, and built-in operations.

---

## Context-Free Grammar (CFG) Production Rules

The GAL compiler uses an LL(1) predictive parser. The grammar has **51 non-terminals** and uses **λ (lambda)** to represent epsilon (empty production).

### Program Structure

```
<program> → <global_declaration> <function_definition> root ( ) { <statement> }
```

### Global Declarations

```
<global_declaration> → bundle id <bundle_or_var> <global_declaration>
                     | <data_type> id <array_dec> <var_value> ; <global_declaration>
                     | fertile <data_type> id = <init_val> <const_next> ; <global_declaration>
                     | λ

<bundle_or_var> → { <bundle_members> } ;
               | <bundle_mem_dec> ;
```

### Data Types

```
<data_type> → seed | tree | leaf | branch | vine
```

### Variable Declarations

```
<var_dec> → <data_type> id <array_dec> <var_value>
          | bundle id <bundle_mem_dec>

<var_value> → = <init_val> <var_value_next>
            | <var_value_next>

<var_value_next> → , id <array_dec> <var_value>
                 | λ
```

### Constant Declarations

```
<const_dec> → fertile <data_type> id = <init_val> <const_next>

<const_next> → , id = <init_val> <const_next>
             | λ
```

### Initialization Values

```
<init_val> → <array_init_opt>
           | water ( <water_arg> )
           | <expression>
```

### Array Declarations

```
<array_dec> → [ <array_dim_opt> ] <array_dec>
            | λ

<array_dim_opt> → intlit | dblit | λ

<array_init_opt> → { <init_vals> }
                 | λ

<init_vals> → <init_val_item> <init_vals_next>
            | λ

<init_vals_next> → , <init_val_item> <init_vals_next>
                 | λ

<init_val_item> → { <init_vals> }
               | <expression>
```

### Bundle (Struct) Declarations

```
<bundle_declaration> → bundle id { <bundle_members> }

<bundle_members> → <data_type> id ; <bundle_members>
                 | id id ; <bundle_members>
                 | λ

<bundle_mem_dec> → id <array_dec> <var_value_next>
                 | , id <var_value_next>
                 | λ
```

### Function Definitions

```
<function_definition> → pollinate <return_type> id ( <parameters> ) { <statement> } <function_definition>
                      | λ

<return_type> → <data_type> | empty | id

<parameters> → <param> <param_next>
             | λ

<param> → <data_type> id <param_array>
        | id id

<param_array> → [ ] | λ

<param_next> → , <param> <param_next>
             | λ
```

### Return Statement

```
<reclaim_opt> → reclaim <reclaim_value>
              | λ

<reclaim_value> → <expression> ;
               | ;
```

### Statements

```
<statement> → <simple_stmt> <statement>
            | λ

<simple_stmt> → id <id_stmt>
              | <inc_dec_op> id ;
              | <io_stmt>
              | <conditional_stmt>
              | <loop_stmt>
              | <switch_stmt>
              | <control_stmt>
              | reclaim <reclaim_value>
              | <var_dec> ;
              | <const_dec> ;

<id_stmt> → <id_next> <assign_op> <assign_rhs> ;
           | <inc_dec_op> ;
           | ( <arguments> ) ;
```

### Assignment

```
<assignment_stmt> → <value> <assign_op> <assign_rhs> ;

<assign_rhs> → water ( <water_arg> )
             | <expression>

<assign_op> → = | += | -= | *= | /= | %=

<value> → id <id_next>

<id_next> → <array_access> <post_array_access>
           | <struct_access>
           | λ
```

### Array Access

```
<array_access> → [ <expression> ] <array_access_more>

<array_access_more> → [ <expression> ] <array_access_more>
                    | λ
```

### Struct/Bundle Access

```
<struct_access> → . id <struct_access_more>

<struct_access_more> → . id <struct_access_more>
                     | λ

<post_array_access> → . id <post_array_access>
                    | λ
```

### Input/Output Statements

```
<io_stmt> → plant ( <arguments> ) ;
          | water ( <water_arg> ) ;

<water_arg> → <data_type>
            | id <water_id_tail>
            | λ

<water_id_tail> → [ <expression> ] <water_id_tail>
               | λ

<arguments> → <expression> <arg_next>
            | λ

<arg_next> → , <expression> <arg_next>
           | λ
```

### Conditional Statements

```
<conditional_stmt> → spring ( <expression> ) { <statement> } <elseif_chain> <else_opt>

<elseif_chain> → bud ( <expression> ) { <statement> } <elseif_chain>
              | λ

<else_opt> → wither { <statement> }
           | λ
```

### Loop Statements

```
<loop_stmt> → grow ( <expression> ) { <statement> }
            | cultivate ( <for_init> ; <expression> ; <for_update> ) { <statement> }
            | tend { <statement> } grow ( <expression> ) ;

<for_init> → <data_type> id <array_dec> <var_value>
           | id <id_next> <assign_op> <expression>
           | λ

<for_update> → id <for_update_type>
             | λ

<for_update_type> → <inc_dec_op>
                  | <id_next> <assign_op> <expression>

<inc_dec_op> → ++ | --
```

### Unary Statement

```
<unary_stmt> → id <inc_dec_op> ;
```

### Switch Statement

```
<switch_stmt> → harvest ( <expression> ) { <case_list> <default_opt> }

<case_list> → variety <case_literal> : <case_statements> <case_list>
            | λ

<case_literal> → intlit | dblit | chrlit | stringlit | sunshine | frost

<case_statements> → <case_statement> <case_statements>
                  | λ

<case_statement> → id <id_stmt>
                 | <inc_dec_op> id ;
                 | <var_dec> ;
                 | <io_stmt>
                 | <conditional_stmt>
                 | <loop_stmt>
                 | <switch_stmt>
                 | { <case_statements> }
                 | prune ;
                 | skip ;
                 | reclaim <reclaim_value>

<default_opt> → soil : <case_statements>
              | λ
```

### Control Flow

```
<control_stmt> → prune ;
               | skip ;

<function_call> → id ( <arguments> ) ;
```

### Expressions (Operator Precedence Encoded)

```
<expression> → <logic_or>

<logic_or> → <logic_and> <logic_or_next>
<logic_or_next> → || <logic_and> <logic_or_next> | λ

<logic_and> → <relational> <logic_and_next>
<logic_and_next> → && <relational> <logic_and_next> | λ

<relational> → <arithmetic> <relational_next>
<relational_next> → <relational_op> <arithmetic> | λ
<relational_op> → > | < | >= | <= | == | !=

<arithmetic> → <term> <arithmetic_next>
<arithmetic_next> → + <term> <arithmetic_next>
                  | - <term> <arithmetic_next>
                  | ` <term> <arithmetic_next>
                  | λ

<term> → <factor> <term_next>
<term_next> → * <factor> <term_next>
            | / <factor> <term_next>
            | % <factor> <term_next>
            | λ

<factor> → ( <paren_expr>
           | <unary_op> <factor>
           | id <factor_id_next>
           | intlit | dblit | chrlit | stringlit | sunshine | frost

<paren_expr> → <data_type> ) <factor>
             | <expression> )

<unary_op> → ~ | !

<factor_id_next> → <array_access> <post_array_access>
                 | <struct_access>
                 | ( <arguments> )
                 | λ
```

---

## Operator Precedence Table

From lowest to highest precedence (encoded in the CFG structure):

| Level | Operators | Description | CFG Rule |
|-------|-----------|-------------|----------|
| 1 (lowest) | `\|\|` | Logical OR | `<logic_or>` |
| 2 | `&&` | Logical AND | `<logic_and>` |
| 3 | `>`, `<`, `>=`, `<=`, `==`, `!=` | Relational comparison | `<relational>` |
| 4 | `+`, `-`, `` ` `` | Addition, subtraction, string concatenation | `<arithmetic>` |
| 5 | `*`, `/`, `%` | Multiplication, division, modulo | `<term>` |
| 6 (highest) | `~`, `!`, `()`, literals, id, function call | Unary, grouping, primary | `<factor>` |

---

## FIRST Sets

FIRST(X) = the set of terminals that can appear at the **beginning** of any string derived from X.

```
First(<program>) = { branch, bundle, fertile, leaf, pollinate, root, seed, tree, vine }
First(<global_declaration>) = { branch, bundle, fertile, leaf, seed, tree, vine, λ }
First(<bundle_or_var>) = { ,, ;, id, { }
First(<declaration>) = { branch, bundle, fertile, leaf, seed, tree, vine, λ }
First(<data_type>) = { branch, leaf, seed, tree, vine }
First(<const_dec>) = { fertile }
First(<const_next>) = { ,, λ }
First(<var_dec>) = { branch, bundle, leaf, seed, tree, vine }
First(<bundle_mem_dec>) = { ,, id, λ }
First(<var_value>) = { ,, =, λ }
First(<var_value_next>) = { ,, λ }
First(<init_val>) = { !, (, chrlit, dblit, frost, id, intlit, stringlit, sunshine, water, {, ~, λ }
First(<array_dec>) = { [, λ }
First(<array_dim_opt>) = { dblit, intlit, λ }
First(<array_init_opt>) = { {, λ }
First(<init_vals>) = { !, (, chrlit, dblit, frost, id, intlit, stringlit, sunshine, {, ~, λ }
First(<init_vals_next>) = { ,, λ }
First(<init_val_item>) = { !, (, chrlit, dblit, frost, id, intlit, stringlit, sunshine, {, ~ }
First(<bundle_declaration>) = { bundle }
First(<bundle_members>) = { branch, id, leaf, seed, tree, vine, λ }
First(<function_definition>) = { pollinate, λ }
First(<return_type>) = { branch, empty, id, leaf, seed, tree, vine }
First(<parameters>) = { branch, id, leaf, seed, tree, vine, λ }
First(<param>) = { branch, id, leaf, seed, tree, vine }
First(<param_array>) = { [, λ }
First(<param_next>) = { ,, λ }
First(<reclaim_opt>) = { reclaim, λ }
First(<reclaim_value>) = { !, (, ;, chrlit, dblit, frost, id, intlit, stringlit, sunshine, ~ }
First(<statement>) = { ++, --, branch, bundle, cultivate, fertile, grow, harvest, id, leaf, plant, prune, reclaim, seed, skip, spring, tend, tree, vine, water, λ }
First(<simple_stmt>) = { ++, --, branch, bundle, cultivate, fertile, grow, harvest, id, leaf, plant, prune, reclaim, seed, skip, spring, tend, tree, vine, water }
First(<id_stmt>) = { %=, (, *=, ++, +=, --, -=, ., /=, =, [ }
First(<assign_rhs>) = { !, (, chrlit, dblit, frost, id, intlit, stringlit, sunshine, water, ~ }
First(<assign_op>) = { %=, *=, +=, -=, /=, = }
First(<value>) = { id }
First(<id_next>) = { ., [, λ }
First(<array_access>) = { [ }
First(<array_access_more>) = { [, λ }
First(<struct_access>) = { . }
First(<struct_access_more>) = { ., λ }
First(<post_array_access>) = { ., λ }
First(<io_stmt>) = { plant, water }
First(<water_arg>) = { branch, id, leaf, seed, tree, vine, λ }
First(<water_id_tail>) = { [, λ }
First(<arguments>) = { !, (, chrlit, dblit, frost, id, intlit, stringlit, sunshine, ~, λ }
First(<arg_next>) = { ,, λ }
First(<conditional_stmt>) = { spring }
First(<elseif_chain>) = { bud, λ }
First(<else_opt>) = { wither, λ }
First(<loop_stmt>) = { cultivate, grow, tend }
First(<for_init>) = { branch, id, leaf, seed, tree, vine, λ }
First(<for_update>) = { id, λ }
First(<for_update_type>) = { %=, *=, ++, +=, --, -=, ., /=, =, [ }
First(<unary_stmt>) = { id }
First(<inc_dec_op>) = { ++, -- }
First(<switch_stmt>) = { harvest }
First(<case_list>) = { variety, λ }
First(<case_literal>) = { chrlit, dblit, frost, intlit, stringlit, sunshine }
First(<case_statements>) = { ++, --, branch, bundle, cultivate, grow, harvest, id, leaf, plant, prune, reclaim, seed, skip, spring, tend, tree, vine, water, {, λ }
First(<case_statement>) = { ++, --, branch, bundle, cultivate, grow, harvest, id, leaf, plant, prune, reclaim, seed, skip, spring, tend, tree, vine, water, { }
First(<default_opt>) = { soil, λ }
First(<control_stmt>) = { prune, skip }
First(<function_call>) = { id }
First(<expression>) = { !, (, chrlit, dblit, frost, id, intlit, stringlit, sunshine, ~ }
First(<logic_or>) = { !, (, chrlit, dblit, frost, id, intlit, stringlit, sunshine, ~ }
First(<logic_or_next>) = { ||, λ }
First(<logic_and>) = { !, (, chrlit, dblit, frost, id, intlit, stringlit, sunshine, ~ }
First(<logic_and_next>) = { &&, λ }
First(<relational>) = { !, (, chrlit, dblit, frost, id, intlit, stringlit, sunshine, ~ }
First(<relational_next>) = { !=, <, <=, ==, >, >=, λ }
First(<relational_op>) = { !=, <, <=, ==, >, >= }
First(<arithmetic>) = { !, (, chrlit, dblit, frost, id, intlit, stringlit, sunshine, ~ }
First(<arithmetic_next>) = { +, -, `, λ }
First(<term>) = { !, (, chrlit, dblit, frost, id, intlit, stringlit, sunshine, ~ }
First(<term_next>) = { %, *, /, λ }
First(<factor>) = { !, (, chrlit, dblit, frost, id, intlit, stringlit, sunshine, ~ }
First(<paren_expr>) = { !, (, branch, chrlit, dblit, frost, id, intlit, leaf, seed, stringlit, sunshine, tree, vine, ~ }
First(<unary_op>) = { !, ~ }
First(<factor_id_next>) = { (, ., [, λ }
First(<assignment_stmt>) = { id }
```

---

## FOLLOW Sets

FOLLOW(X) = the set of terminals that can appear **immediately after** X in any derivation.

```
Follow(<program>) = { EOF }
Follow(<global_declaration>) = { pollinate, root }
Follow(<function_definition>) = { root }
Follow(<statement>) = { } }
Follow(<bundle_or_var>) = { branch, bundle, fertile, leaf, pollinate, root, seed, tree, vine }
Follow(<data_type>) = { ), id }
Follow(<array_dec>) = { ,, ;, = }
Follow(<var_value>) = { ; }
Follow(<init_val>) = { ,, ; }
Follow(<const_next>) = { ; }
Follow(<bundle_members>) = { } }
Follow(<bundle_mem_dec>) = { ; }
Follow(<var_dec>) = { ; }
Follow(<const_dec>) = { ; }
Follow(<var_value_next>) = { ; }
Follow(<array_init_opt>) = { ,, ; }
Follow(<water_arg>) = { ) }
Follow(<expression>) = { ), ,, ;, ], } }
Follow(<array_dim_opt>) = { ] }
Follow(<init_vals>) = { } }
Follow(<init_val_item>) = { ,, } }
Follow(<init_vals_next>) = { } }
Follow(<return_type>) = { id }
Follow(<parameters>) = { ) }
Follow(<param>) = { ), , }
Follow(<param_next>) = { ) }
Follow(<param_array>) = { ), , }
Follow(<reclaim_value>) = { ++, --, branch, bundle, cultivate, fertile, grow, harvest, id, leaf, plant, prune, reclaim, seed, skip, soil, spring, tend, tree, variety, vine, water, {, } }
Follow(<simple_stmt>) = { ++, --, branch, bundle, cultivate, fertile, grow, harvest, id, leaf, plant, prune, reclaim, seed, skip, spring, tend, tree, vine, water, } }
Follow(<id_stmt>) = { ++, --, branch, bundle, cultivate, fertile, grow, harvest, id, leaf, plant, prune, reclaim, seed, skip, soil, spring, tend, tree, variety, vine, water, {, } }
Follow(<inc_dec_op>) = { ), ;, id }
Follow(<io_stmt>) = { ++, --, branch, bundle, cultivate, fertile, grow, harvest, id, leaf, plant, prune, reclaim, seed, skip, soil, spring, tend, tree, variety, vine, water, {, } }
Follow(<conditional_stmt>) = { ++, --, branch, bundle, cultivate, fertile, grow, harvest, id, leaf, plant, prune, reclaim, seed, skip, soil, spring, tend, tree, variety, vine, water, {, } }
Follow(<loop_stmt>) = { ++, --, branch, bundle, cultivate, fertile, grow, harvest, id, leaf, plant, prune, reclaim, seed, skip, soil, spring, tend, tree, variety, vine, water, {, } }
Follow(<switch_stmt>) = { ++, --, branch, bundle, cultivate, fertile, grow, harvest, id, leaf, plant, prune, reclaim, seed, skip, soil, spring, tend, tree, variety, vine, water, {, } }
Follow(<control_stmt>) = { ++, --, branch, bundle, cultivate, fertile, grow, harvest, id, leaf, plant, prune, reclaim, seed, skip, spring, tend, tree, vine, water, } }
Follow(<id_next>) = { %=, *=, +=, -=, /=, = }
Follow(<assign_op>) = { !, (, chrlit, dblit, frost, id, intlit, stringlit, sunshine, water, ~ }
Follow(<assign_rhs>) = { ; }
Follow(<arguments>) = { ) }
Follow(<value>) = { %=, *=, +=, -=, /=, = }
Follow(<array_access>) = { !=, %, %=, &&, ), *, *=, +, +=, ,, -, -=, ., /, /=, ;, <, <=, =, ==, >, >=, ], `, ||, } }
Follow(<post_array_access>) = { !=, %, %=, &&, ), *, *=, +, +=, ,, -, -=, /, /=, ;, <, <=, =, ==, >, >=, ], `, ||, } }
Follow(<struct_access>) = { !=, %, %=, &&, ), *, *=, +, +=, ,, -, -=, /, /=, ;, <, <=, =, ==, >, >=, ], `, ||, } }
Follow(<array_access_more>) = { !=, %, %=, &&, ), *, *=, +, +=, ,, -, -=, ., /, /=, ;, <, <=, =, ==, >, >=, ], `, ||, } }
Follow(<struct_access_more>) = { !=, %, %=, &&, ), *, *=, +, +=, ,, -, -=, /, /=, ;, <, <=, =, ==, >, >=, ], `, ||, } }
Follow(<water_id_tail>) = { ) }
Follow(<arg_next>) = { ) }
Follow(<elseif_chain>) = { ++, --, branch, bundle, cultivate, fertile, grow, harvest, id, leaf, plant, prune, reclaim, seed, skip, soil, spring, tend, tree, variety, vine, water, wither, {, } }
Follow(<else_opt>) = { ++, --, branch, bundle, cultivate, fertile, grow, harvest, id, leaf, plant, prune, reclaim, seed, skip, soil, spring, tend, tree, variety, vine, water, {, } }
Follow(<for_init>) = { ; }
Follow(<for_update>) = { ) }
Follow(<for_update_type>) = { ) }
Follow(<case_list>) = { soil, } }
Follow(<default_opt>) = { } }
Follow(<case_literal>) = { : }
Follow(<case_statements>) = { soil, variety, } }
Follow(<case_statement>) = { ++, --, branch, bundle, cultivate, grow, harvest, id, leaf, plant, prune, reclaim, seed, skip, soil, spring, tend, tree, variety, vine, water, {, } }
Follow(<logic_or>) = { ), ,, ;, ], } }
Follow(<logic_and>) = { ), ,, ;, ], ||, } }
Follow(<logic_or_next>) = { ), ,, ;, ], } }
Follow(<relational>) = { &&, ), ,, ;, ], ||, } }
Follow(<logic_and_next>) = { ), ,, ;, ], ||, } }
Follow(<arithmetic>) = { !=, &&, ), ,, ;, <, <=, ==, >, >=, ], ||, } }
Follow(<relational_next>) = { &&, ), ,, ;, ], ||, } }
Follow(<relational_op>) = { !, (, chrlit, dblit, frost, id, intlit, stringlit, sunshine, ~ }
Follow(<term>) = { !=, &&, ), +, ,, -, ;, <, <=, ==, >, >=, ], `, ||, } }
Follow(<arithmetic_next>) = { !=, &&, ), ,, ;, <, <=, ==, >, >=, ], ||, } }
Follow(<factor>) = { !=, %, &&, ), *, +, ,, -, /, ;, <, <=, ==, >, >=, ], `, ||, } }
Follow(<term_next>) = { !=, &&, ), +, ,, -, ;, <, <=, ==, >, >=, ], `, ||, } }
Follow(<paren_expr>) = { !=, %, &&, ), *, +, ,, -, /, ;, <, <=, ==, >, >=, ], `, ||, } }
Follow(<unary_op>) = { !, (, chrlit, dblit, frost, id, intlit, stringlit, sunshine, ~ }
Follow(<factor_id_next>) = { !=, %, &&, ), *, +, ,, -, /, ;, <, <=, ==, >, >=, ], `, ||, } }
```

---

## PREDICT Sets

PREDICT(A → α) = the set of terminals that indicate when to use production A → α during parsing.

### Program Structure
```
Predict(<program> → <global_declaration> <function_definition> root ( ) { <statement> }) = { branch, bundle, fertile, leaf, pollinate, root, seed, tree, vine }
```

### Global Declarations
```
Predict(<global_declaration> → bundle id <bundle_or_var> <global_declaration>) = { bundle }
Predict(<global_declaration> → <data_type> id <array_dec> <var_value> ; <global_declaration>) = { branch, leaf, seed, tree, vine }
Predict(<global_declaration> → fertile <data_type> id = <init_val> <const_next> ; <global_declaration>) = { fertile }
Predict(<global_declaration> → λ) = { pollinate, root }
Predict(<bundle_or_var> → { <bundle_members> } ;) = { { }
Predict(<bundle_or_var> → <bundle_mem_dec> ;) = { ,, ;, id }
```

### Declarations
```
Predict(<declaration> → <var_dec> ; <declaration>) = { branch, bundle, leaf, seed, tree, vine }
Predict(<declaration> → <const_dec> ; <declaration>) = { fertile }
Predict(<declaration> → λ) = { }
```

### Data Types
```
Predict(<data_type> → seed) = { seed }
Predict(<data_type> → tree) = { tree }
Predict(<data_type> → leaf) = { leaf }
Predict(<data_type> → branch) = { branch }
Predict(<data_type> → vine) = { vine }
```

### Constants
```
Predict(<const_dec> → fertile <data_type> id = <init_val> <const_next>) = { fertile }
Predict(<const_next> → , id = <init_val> <const_next>) = { , }
Predict(<const_next> → λ) = { ; }
```

### Variables
```
Predict(<var_dec> → <data_type> id <array_dec> <var_value>) = { branch, leaf, seed, tree, vine }
Predict(<var_dec> → bundle id <bundle_mem_dec>) = { bundle }
Predict(<bundle_mem_dec> → id <array_dec> <var_value_next>) = { id }
Predict(<bundle_mem_dec> → , id <var_value_next>) = { , }
Predict(<bundle_mem_dec> → λ) = { ; }
Predict(<var_value> → = <init_val> <var_value_next>) = { = }
Predict(<var_value> → <var_value_next>) = { ,, ;, λ }
Predict(<var_value_next> → , id <array_dec> <var_value>) = { , }
Predict(<var_value_next> → λ) = { ; }
```

### Initialization
```
Predict(<init_val> → <array_init_opt>) = { ,, ;, {, λ }
Predict(<init_val> → water ( <water_arg> )) = { water }
Predict(<init_val> → <expression>) = { !, (, chrlit, dblit, frost, id, intlit, stringlit, sunshine, ~ }
```

### Arrays
```
Predict(<array_dec> → [ <array_dim_opt> ] <array_dec>) = { [ }
Predict(<array_dec> → λ) = { ,, ;, = }
Predict(<array_dim_opt> → intlit) = { intlit }
Predict(<array_dim_opt> → dblit) = { dblit }
Predict(<array_dim_opt> → λ) = { ] }
Predict(<array_init_opt> → { <init_vals> }) = { { }
Predict(<array_init_opt> → λ) = { ,, ; }
Predict(<init_vals> → <init_val_item> <init_vals_next>) = { !, (, chrlit, dblit, frost, id, intlit, stringlit, sunshine, {, ~ }
Predict(<init_vals> → λ) = { } }
Predict(<init_vals_next> → , <init_val_item> <init_vals_next>) = { , }
Predict(<init_vals_next> → λ) = { } }
Predict(<init_val_item> → { <init_vals> }) = { { }
Predict(<init_val_item> → <expression>) = { !, (, chrlit, dblit, frost, id, intlit, stringlit, sunshine, ~ }
```

### Bundles (Structs)
```
Predict(<bundle_declaration> → bundle id { <bundle_members> }) = { bundle }
Predict(<bundle_members> → <data_type> id ; <bundle_members>) = { branch, leaf, seed, tree, vine }
Predict(<bundle_members> → id id ; <bundle_members>) = { id }
Predict(<bundle_members> → λ) = { } }
```

### Functions
```
Predict(<function_definition> → pollinate <return_type> id ( <parameters> ) { <statement> } <function_definition>) = { pollinate }
Predict(<function_definition> → λ) = { root }
Predict(<return_type> → <data_type>) = { branch, leaf, seed, tree, vine }
Predict(<return_type> → empty) = { empty }
Predict(<return_type> → id) = { id }
Predict(<parameters> → λ) = { ) }
Predict(<parameters> → <param> <param_next>) = { branch, id, leaf, seed, tree, vine }
Predict(<param> → <data_type> id <param_array>) = { branch, leaf, seed, tree, vine }
Predict(<param> → id id) = { id }
Predict(<param_array> → λ) = { ), , }
Predict(<param_array> → [ ]) = { [ }
Predict(<param_next> → λ) = { ) }
Predict(<param_next> → , <param> <param_next>) = { , }
```

### Return
```
Predict(<reclaim_opt> → reclaim <reclaim_value>) = { reclaim }
Predict(<reclaim_opt> → λ) = { }
Predict(<reclaim_value> → <expression> ;) = { !, (, chrlit, dblit, frost, id, intlit, stringlit, sunshine, ~ }
Predict(<reclaim_value> → ;) = { ; }
```

### Statements
```
Predict(<statement> → <simple_stmt> <statement>) = { ++, --, branch, bundle, cultivate, fertile, grow, harvest, id, leaf, plant, prune, reclaim, seed, skip, spring, tend, tree, vine, water }
Predict(<statement> → λ) = { } }
Predict(<simple_stmt> → id <id_stmt>) = { id }
Predict(<simple_stmt> → <inc_dec_op> id ;) = { ++, -- }
Predict(<simple_stmt> → <io_stmt>) = { plant, water }
Predict(<simple_stmt> → <conditional_stmt>) = { spring }
Predict(<simple_stmt> → <loop_stmt>) = { cultivate, grow, tend }
Predict(<simple_stmt> → <switch_stmt>) = { harvest }
Predict(<simple_stmt> → <control_stmt>) = { prune, skip }
Predict(<simple_stmt> → reclaim <reclaim_value>) = { reclaim }
Predict(<simple_stmt> → <var_dec> ;) = { branch, bundle, leaf, seed, tree, vine }
Predict(<simple_stmt> → <const_dec> ;) = { fertile }
Predict(<id_stmt> → <id_next> <assign_op> <assign_rhs> ;) = { %=, *=, +=, -=, ., /=, =, [ }
Predict(<id_stmt> → <inc_dec_op> ;) = { ++, -- }
Predict(<id_stmt> → ( <arguments> ) ;) = { ( }
```

### Assignment
```
Predict(<assignment_stmt> → <value> <assign_op> <assign_rhs> ;) = { id }
Predict(<assign_rhs> → water ( <water_arg> )) = { water }
Predict(<assign_rhs> → <expression>) = { !, (, chrlit, dblit, frost, id, intlit, stringlit, sunshine, ~ }
Predict(<assign_op> → =) = { = }
Predict(<assign_op> → +=) = { += }
Predict(<assign_op> → -=) = { -= }
Predict(<assign_op> → *=) = { *= }
Predict(<assign_op> → /=) = { /= }
Predict(<assign_op> → %=) = { %= }
Predict(<value> → id <id_next>) = { id }
Predict(<id_next> → <array_access> <post_array_access>) = { [ }
Predict(<id_next> → <struct_access>) = { . }
Predict(<id_next> → λ) = { %=, *=, +=, -=, /=, = }
```

### Array/Struct Access
```
Predict(<array_access> → [ <expression> ] <array_access_more>) = { [ }
Predict(<array_access_more> → [ <expression> ] <array_access_more>) = { [ }
Predict(<array_access_more> → λ) = { !=, %, %=, &&, ), *, *=, +, +=, ,, -, -=, ., /, /=, ;, <, <=, =, ==, >, >=, ], `, ||, } }
Predict(<struct_access> → . id <struct_access_more>) = { . }
Predict(<struct_access_more> → . id <struct_access_more>) = { . }
Predict(<struct_access_more> → λ) = { !=, %, %=, &&, ), *, *=, +, +=, ,, -, -=, /, /=, ;, <, <=, =, ==, >, >=, ], `, ||, } }
Predict(<post_array_access> → . id <post_array_access>) = { . }
Predict(<post_array_access> → λ) = { !=, %, %=, &&, ), *, *=, +, +=, ,, -, -=, /, /=, ;, <, <=, =, ==, >, >=, ], `, ||, } }
```

### I/O
```
Predict(<io_stmt> → plant ( <arguments> ) ;) = { plant }
Predict(<io_stmt> → water ( <water_arg> ) ;) = { water }
Predict(<water_arg> → <data_type>) = { branch, leaf, seed, tree, vine }
Predict(<water_arg> → id <water_id_tail>) = { id }
Predict(<water_arg> → λ) = { ) }
Predict(<water_id_tail> → [ <expression> ] <water_id_tail>) = { [ }
Predict(<water_id_tail> → λ) = { ) }
Predict(<arguments> → <expression> <arg_next>) = { !, (, chrlit, dblit, frost, id, intlit, stringlit, sunshine, ~ }
Predict(<arguments> → λ) = { ) }
Predict(<arg_next> → , <expression> <arg_next>) = { , }
Predict(<arg_next> → λ) = { ) }
```

### Conditionals
```
Predict(<conditional_stmt> → spring ( <expression> ) { <statement> } <elseif_chain> <else_opt>) = { spring }
Predict(<elseif_chain> → bud ( <expression> ) { <statement> } <elseif_chain>) = { bud }
Predict(<elseif_chain> → λ) = { ++, --, branch, bundle, cultivate, fertile, grow, harvest, id, leaf, plant, prune, reclaim, seed, skip, soil, spring, tend, tree, variety, vine, water, wither, {, } }
Predict(<else_opt> → wither { <statement> }) = { wither }
Predict(<else_opt> → λ) = { ++, --, branch, bundle, cultivate, fertile, grow, harvest, id, leaf, plant, prune, reclaim, seed, skip, soil, spring, tend, tree, variety, vine, water, {, } }
```

### Loops
```
Predict(<loop_stmt> → grow ( <expression> ) { <statement> }) = { grow }
Predict(<loop_stmt> → cultivate ( <for_init> ; <expression> ; <for_update> ) { <statement> }) = { cultivate }
Predict(<loop_stmt> → tend { <statement> } grow ( <expression> ) ;) = { tend }
Predict(<for_init> → <data_type> id <array_dec> <var_value>) = { branch, leaf, seed, tree, vine }
Predict(<for_init> → id <id_next> <assign_op> <expression>) = { id }
Predict(<for_init> → λ) = { ; }
Predict(<for_update> → id <for_update_type>) = { id }
Predict(<for_update> → λ) = { ) }
Predict(<for_update_type> → <inc_dec_op>) = { ++, -- }
Predict(<for_update_type> → <id_next> <assign_op> <expression>) = { %=, *=, +=, -=, ., /=, =, [ }
Predict(<inc_dec_op> → ++) = { ++ }
Predict(<inc_dec_op> → --) = { -- }
```

### Switch
```
Predict(<switch_stmt> → harvest ( <expression> ) { <case_list> <default_opt> }) = { harvest }
Predict(<case_list> → variety <case_literal> : <case_statements> <case_list>) = { variety }
Predict(<case_list> → λ) = { soil, } }
Predict(<case_literal> → intlit) = { intlit }
Predict(<case_literal> → dblit) = { dblit }
Predict(<case_literal> → chrlit) = { chrlit }
Predict(<case_literal> → stringlit) = { stringlit }
Predict(<case_literal> → sunshine) = { sunshine }
Predict(<case_literal> → frost) = { frost }
Predict(<case_statements> → <case_statement> <case_statements>) = { ++, --, branch, bundle, cultivate, grow, harvest, id, leaf, plant, prune, reclaim, seed, skip, spring, tend, tree, vine, water, { }
Predict(<case_statements> → λ) = { soil, variety, } }
Predict(<case_statement> → id <id_stmt>) = { id }
Predict(<case_statement> → <inc_dec_op> id ;) = { ++, -- }
Predict(<case_statement> → <var_dec> ;) = { branch, bundle, leaf, seed, tree, vine }
Predict(<case_statement> → <io_stmt>) = { plant, water }
Predict(<case_statement> → <conditional_stmt>) = { spring }
Predict(<case_statement> → <loop_stmt>) = { cultivate, grow, tend }
Predict(<case_statement> → <switch_stmt>) = { harvest }
Predict(<case_statement> → { <case_statements> }) = { { }
Predict(<case_statement> → prune ;) = { prune }
Predict(<case_statement> → skip ;) = { skip }
Predict(<case_statement> → reclaim <reclaim_value>) = { reclaim }
Predict(<default_opt> → soil : <case_statements>) = { soil }
Predict(<default_opt> → λ) = { } }
```

### Control Flow
```
Predict(<control_stmt> → prune ;) = { prune }
Predict(<control_stmt> → skip ;) = { skip }
Predict(<function_call> → id ( <arguments> ) ;) = { id }
```

### Expressions
```
Predict(<expression> → <logic_or>) = { !, (, chrlit, dblit, frost, id, intlit, stringlit, sunshine, ~ }
Predict(<logic_or> → <logic_and> <logic_or_next>) = { !, (, chrlit, dblit, frost, id, intlit, stringlit, sunshine, ~ }
Predict(<logic_or_next> → || <logic_and> <logic_or_next>) = { || }
Predict(<logic_or_next> → λ) = { ), ,, ;, ], } }
Predict(<logic_and> → <relational> <logic_and_next>) = { !, (, chrlit, dblit, frost, id, intlit, stringlit, sunshine, ~ }
Predict(<logic_and_next> → && <relational> <logic_and_next>) = { && }
Predict(<logic_and_next> → λ) = { ), ,, ;, ], ||, } }
Predict(<relational> → <arithmetic> <relational_next>) = { !, (, chrlit, dblit, frost, id, intlit, stringlit, sunshine, ~ }
Predict(<relational_next> → <relational_op> <arithmetic>) = { !=, <, <=, ==, >, >= }
Predict(<relational_next> → λ) = { &&, ), ,, ;, ], ||, } }
Predict(<relational_op> → >) = { > }
Predict(<relational_op> → <) = { < }
Predict(<relational_op> → >=) = { >= }
Predict(<relational_op> → <=) = { <= }
Predict(<relational_op> → ==) = { == }
Predict(<relational_op> → !=) = { != }
Predict(<arithmetic> → <term> <arithmetic_next>) = { !, (, chrlit, dblit, frost, id, intlit, stringlit, sunshine, ~ }
Predict(<arithmetic_next> → + <term> <arithmetic_next>) = { + }
Predict(<arithmetic_next> → - <term> <arithmetic_next>) = { - }
Predict(<arithmetic_next> → ` <term> <arithmetic_next>) = { ` }
Predict(<arithmetic_next> → λ) = { !=, &&, ), ,, ;, <, <=, ==, >, >=, ], ||, } }
Predict(<term> → <factor> <term_next>) = { !, (, chrlit, dblit, frost, id, intlit, stringlit, sunshine, ~ }
Predict(<term_next> → * <factor> <term_next>) = { * }
Predict(<term_next> → / <factor> <term_next>) = { / }
Predict(<term_next> → % <factor> <term_next>) = { % }
Predict(<term_next> → λ) = { !=, &&, ), +, ,, -, ;, <, <=, ==, >, >=, ], `, ||, } }
Predict(<factor> → ( <paren_expr>) = { ( }
Predict(<factor> → <unary_op> <factor>) = { !, ~ }
Predict(<factor> → id <factor_id_next>) = { id }
Predict(<factor> → intlit) = { intlit }
Predict(<factor> → dblit) = { dblit }
Predict(<factor> → chrlit) = { chrlit }
Predict(<factor> → stringlit) = { stringlit }
Predict(<factor> → sunshine) = { sunshine }
Predict(<factor> → frost) = { frost }
Predict(<paren_expr> → <data_type> ) <factor>) = { branch, leaf, seed, tree, vine }
Predict(<paren_expr> → <expression> )) = { !, (, chrlit, dblit, frost, id, intlit, stringlit, sunshine, ~ }
Predict(<unary_op> → ~) = { ~ }
Predict(<unary_op> → !) = { ! }
Predict(<factor_id_next> → <array_access> <post_array_access>) = { [ }
Predict(<factor_id_next> → <struct_access>) = { . }
Predict(<factor_id_next> → ( <arguments> )) = { ( }
Predict(<factor_id_next> → λ) = { !=, %, &&, ), *, +, ,, -, /, ;, <, <=, ==, >, >=, ], `, ||, } }
```

---

## Semantic Rules

The semantic analyzer (`GALsemantic.py`) enforces these rules during AST construction:

### Variable Rules
1. **Declaration before use** — A variable must be declared before it is referenced. Using an undeclared variable produces: `Semantic Error: Variable 'x' used before declaration.`
2. **No duplicate declarations** — A variable cannot be declared twice in the same scope. Produces: `Semantic Error: Variable 'x' already declared.`
3. **Constant immutability** — Variables declared with `fertile` cannot be reassigned after initialization.
4. **Scope management** — Variables are scoped to their enclosing block (`{ }`). Inner scopes can shadow outer variables. Scopes are pushed on entry and popped on exit.

### Function Rules
5. **No duplicate functions** — A function cannot be declared twice. Produces: `Semantic Error: Function 'foo' already declared.`
6. **Function must exist** — Calling an undefined function produces: `Semantic Error: Function 'foo' is not defined.`
7. **Variable-function conflict** — A variable name cannot clash with a function name. Produces: `Semantic Error: Variable 'x' already declared as a function.`

### Bundle (Struct) Rules
8. **No duplicate bundle types** — A bundle type cannot be defined twice. Produces: `Semantic Error: Bundle type 'Person' already defined.`
9. **No duplicate members** — A bundle cannot have two members with the same name. Produces: `Semantic Error: Duplicate member 'age' in bundle 'Person'.`
10. **Bundle type must exist** — Using an undefined bundle type produces: `Semantic Error: Bundle type 'Person' is not defined.`

### Type System
11. **Type casting** — Explicit casts are supported: `(seed)x`, `(tree)x`, `(leaf)x`, `(vine)x`, `(branch)x`.
12. **Format string** — `plant()` supports format strings with `{}` placeholders: `plant("x = {}\n", x);`

---

## AST Node Types

The Abstract Syntax Tree (AST) is built from these node types (defined in `GALsemantic.py`):

| Node Type | Description | Example |
|-----------|-------------|---------|
| `ProgramNode` | Root of the AST | Entire program |
| `VariableDeclarationNode` | Variable declaration | `seed x = 5;` |
| `AssignmentNode` | Variable assignment | `x = 10;` |
| `BinaryOpNode` | Binary operation | `a + b`, `x == y` |
| `UnaryOpNode` | Unary operation | `~x`, `!flag` |
| `FunctionDeclarationNode` | Function definition | `pollinate seed add(...)` |
| `FunctionCallNode` | Function call | `add(2, 3)` |
| `IfStatementNode` | If/else-if/else | `spring (x > 0) { ... }` |
| `ForLoopNode` | For loop | `cultivate (seed i = 0; ...) { ... }` |
| `WhileLoopNode` | While loop | `grow (x < 10) { ... }` |
| `DoWhileLoopNode` | Do-while loop | `tend { ... } grow (x < 10);` |
| `PrintNode` | Print statement | `plant("hello\n");` |
| `ReturnNode` | Return statement | `reclaim x;` |
| `SwitchNode` | Switch statement | `harvest (choice) { ... }` |
| `ContinueNode` | Continue | `skip;` |
| `BreakNode` | Break | `prune;` |
| `FertileDeclarationNode` | Constant declaration | `fertile seed MAX = 100;` |
| `UpdateNode` | Increment/decrement | `x++`, `--y` |
| `CastNode` | Type cast | `(seed)x` |
| `ListNode` | Array literal | `{1, 2, 3}` |
| `ListAccessNode` | Array indexing | `arr[0]`, `word[i]` |
| `MemberAccessNode` | Struct member | `person.age` |
| `ArrayMemberAccessNode` | Array element member | `p[0].x` |
| `BundleDefinitionNode` | Struct definition | `bundle Person { ... }` |
| `TSNode` | Length built-in | `arr.ts`, `word.ts` |
| `TaperNode` | Pop last element | `arr.taper` |
| `SoilNode` | To lowercase | `word.wilt` |
| `BloomNode` | To uppercase | `word.bloom` |
| `AppendNode` | Array append | `arr.append(5)` |
| `InsertNode` | Array insert | `arr.insert(0, 5)` |
| `RemoveNode` | Array remove | `arr.remove(0)` |

---

## Built-in Operations

These are runtime built-in operations handled by the interpreter (`GALinterpreter.py`):

### String Operations
| Operation | Syntax | Description | Example |
|-----------|--------|-------------|---------|
| Length | `word.ts` | Returns the length of a vine string | `vine s = "hello"; plant("{}\n", s.ts);` → `5` |
| Lowercase | `word.wilt` | Returns the string converted to lowercase | `vine s = "HELLO"; plant("{}\n", s.wilt);` → `hello` |
| Uppercase | `word.bloom` | Returns the string converted to uppercase | `vine s = "hello"; plant("{}\n", s.bloom);` → `HELLO` |
| Indexing | `word[i]` | Access character at index i (read/write) | `vine s = "hello"; plant("{}\n", s[0]);` → `h` |
| Concatenation | `a `` ` `` b` | Joins two strings | `vine s = "hi" `` ` `` " there";` → `"hi there"` |

### Array Operations
| Operation | Syntax | Description | Example |
|-----------|--------|-------------|---------|
| Length | `arr.ts` | Returns the number of elements | `seed arr[] = {1,2,3}; plant("{}\n", arr.ts);` → `3` |
| Append | `arr.append(val)` | Adds element to end of array | `arr.append(4);` |
| Insert | `arr.insert(i, val)` | Inserts element at index i | `arr.insert(0, 99);` |
| Remove | `arr.remove(i)` | Removes element at index i | `arr.remove(0);` |
| Pop last | `arr.taper` | Removes and returns last element | `seed last = arr.taper;` |
| Indexing | `arr[i]` | Access element at index i | `arr[0] = 5;` |

### Type Casting
| Cast | Example | Description |
|------|---------|-------------|
| `(seed)x` | `seed n = (seed)3.14;` | Cast to integer (truncates) |
| `(tree)x` | `tree f = (tree)5;` | Cast to float |
| `(leaf)x` | `leaf c = (leaf)65;` | Cast integer to character (ASCII) |
| `(vine)x` | `vine s = (vine)(leaf)65;` | Cast to string |
| `(branch)x` | `branch b = (branch)1;` | Cast to boolean |

---

*End of Document*
