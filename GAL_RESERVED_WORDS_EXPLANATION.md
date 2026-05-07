# GAL Reserved Words and Data Types Explained

This file explains how GAL reserved words work, especially the data types and the most important language keywords. The idea is to make the GAL language easy to read and use.

## What are reserved words?

Reserved words are special words that the GAL compiler already uses for language features. You cannot use them as variable names because the compiler treats them differently.

Examples of reserved words in GAL:
- `seed`, `tree`, `leaf`, `vine`, `branch` — data type keywords
- `root`, `pollinate`, `harvest`, `variety`, `soil` — program structure keywords
- `plant`, `water`, `spring`, `bud`, `grow`, `cultivate`, `tend` — statements and flow control
- `skip`, `prune`, `bundle`, `fertile`, `reclaim` — control, struct, and return keywords

## GAL data types

GAL has five main primitive data types. Each type is declared by a reserved word.

1. `seed` — integer type
   - Use it for whole numbers like 1, 2, -5, 100.
   - Example:
     ```gal
     seed age;
     seed count = 10;
     ```

2. `tree` — floating-point number type
   - Use it for decimal values like 3.14, 2.0, 0.5.
   - Example:
     ```gal
     tree price;
     tree average = 3.5;
     ```

3. `leaf` — character type
   - Use it for a single letter or symbol, like `'A'` or `'\n'`.
   - Example:
     ```gal
     leaf letter = 'X';
     leaf newline = '\n';
     ```

4. `vine` — string type
   - Use it for text strings like `"hello"`.
   - Example:
     ```gal
     vine name;
     vine greeting = "Hello, garden!";
     ```

5. `branch` — boolean type
   - Use it for true/false decisions.
   - Example:
     ```gal
     branch done = false;
     branch passed = true;
     ```

## Example: declaring variables

```gal
root() {
    seed score = 100;
    tree temperature = 25.7;
    leaf symbol = 'G';
    vine message = "Hi";
    branch isReady = true;
    reclaim;
}
```

## Built-in statement keywords and what they do

### `root()`
- The main function of every GAL program.
- The program starts here.
- Like `main()` in C.

Example:
```gal
root() {
    plant("Start\n");
    reclaim;
}
```

### `pollinate` and `empty`
- `pollinate` declares a user-defined function.
- `empty` means the function returns nothing (void).

Example:
```gal
pollinate empty sayHi() {
    plant("Hi\n");
    reclaim;
}
```

### `plant()`
- Prints output to the screen.
- Does not add a newline automatically.
- If you want a new line, include `\n` inside the string.

Example:
```gal
plant("Hello");
plant("\n");
```

### `water()`
- Reads user input.
- You can use it directly on a variable or give it a type.

Examples:
```gal
seed x;
water(x);

seed y = water(seed);
```

### `spring`, `bud`, `wither`
- `spring` is GAL's `if` statement.
- `bud` is `else if`.
- `wither` is `else`.

Example:
```gal
spring (x > 0) {
    plant("Positive\n");
} bud (x < 0) {
    plant("Negative\n");
} wither {
    plant("Zero\n");
}
```

### `grow`, `cultivate`, `tend`
- `grow` is a while loop.
- `cultivate` is a for loop.
- `tend` is a do-while loop.

Examples:
```gal
grow (i < 5) {
    plant(i);
    i = i + 1;
}

cultivate (seed i = 0; i < 5; i++) {
    plant(i);
}

tend {
    plant("Loop once first\n");
    i = i + 1;
} grow (i < 5);
```

### `harvest`, `variety`, `soil`
- `harvest` is like `switch`.
- `variety` is like `case`.
- `soil` is like `default`.

Example:
```gal
harvest (choice) {
    variety (1): plant("One\n"); prune;
    variety (2): plant("Two\n"); prune;
    soil: plant("Other\n");
}
```

### `skip` and `prune`
- `skip` is `continue` inside loops.
- `prune` is `break` inside loops or switch cases.

Example:
```gal
grow (i < 10) {
    i = i + 1;
    if (i == 5) skip;
    if (i == 8) prune;
}
```

## Type casting in GAL

You can convert values from one type to another using a type name in parentheses.

Examples:
```gal
seed x = 3;
tree y = (tree)x;   // convert integer to float
vine s = "7";
seed n = (seed)3.9; // convert float to integer
```

## Arrays
- Declare with square brackets.
- Example:
```gal
seed numbers[5];
seed values[] = {1, 2, 3};
```

Arrays can store many values of the same type, like a list of integers or a list of strings.

## Bundles (Structs)
- `bundle` defines a new structured type with named fields.
- It is like a `struct` in C or a record in other languages.
- After defining a bundle type, you can declare variables that use it.

Example:
```gal
bundle Person {
    seed age;
    vine name;
};

Person p;
```

Explanation:
- `bundle Person { ... };` creates a new type named `Person`.
- Inside the bundle, each field has a type (`seed`, `vine`, etc.) and a name.
- `Person p;` declares a variable `p` of that bundle type.

### Accessing bundle members
Use `.` to get or set fields inside a bundle.

Example:
```gal
p.age = 20;
p.name = "Alice";
plant(p.name);
```

This means:
- `p.age` is the `age` field of the `Person` bundle variable `p`.
- `p.name` is the `name` field.

### Nested bundles
Bundles can contain other bundles as fields.

Example:
```gal
bundle Address {
    seed house;
    vine street;
};

bundle Person {
    seed age;
    vine name;
    Address addr;
};

Person p;
p.addr.house = 10;
p.addr.street = "Garden Lane";
```

This uses `.` twice to access nested fields: `p.addr.house` and `p.addr.street`.

## Functions in GAL
GAL uses `pollinate` to declare functions other than `root()`.

### Basic function declaration
```gal
pollinate seed add(seed a, seed b) {
    reclaim a + b;
}
```

Explanation:
- `pollinate` starts the function declaration.
- `seed` before the name is the return type.
- `add` is the function name.
- `(seed a, seed b)` lists parameter types and names.
- The body is inside `{ ... }`.
- `reclaim a + b;` returns the result from the function.

### Empty / void functions
If the function does not return a value, use `empty`.

Example:
```gal
pollinate empty sayHi(vine name) {
    plant("Hello, ");
    plant(name);
    plant("\n");
    reclaim;
}
```

Explanation:
- `empty` means no value is returned.
- `reclaim;` ends the function.
- You cannot return a value from an `empty` function.

### Calling functions
Use the function name with arguments.

Example:
```gal
seed result = add(3, 4);
plant(result);
```

### `root()` vs `pollinate`
- `root()` is the program entry point. Every GAL program must have exactly one `root()`.
- `pollinate` defines helper functions that `root()` or other functions can call.
- `root()` also ends with `reclaim;`.

Example with both:
```gal
pollinate seed square(seed x) {
    reclaim x * x;
}

root() {
    seed n = 5;
    seed answer = square(n);
    plant(answer);
    reclaim;
}
```

## Complete Program Example: Find Prime Numbers

```gal
pollinate branch isPrime(seed n) {
    seed i;
    seed divisor;

    spring (n < 2) {
        reclaim false;
    }

    cultivate (i = 2; i * i <= n; i++) {
        divisor = n % i;
        spring (divisor == 0) {
            reclaim false;
        }
    }

    reclaim true;
}

root() {
    seed limit;
    seed num;
    branch prime;

    plant("Find primes up to: ");
    water(limit);
    plant("Prime numbers:\n");

    cultivate (num = 2; num <= limit; num++) {
        prime = isPrime(num);
        spring (prime) {
            plant(num);
            plant(" ");
        }
    }

    plant("\n");
    reclaim;
}
```

This program:
1. Defines a helper function `isPrime()` that returns true if a number is prime.
2. In `root()`, asks the user for a limit.
3. Loops through all numbers up to the limit.
4. Calls `isPrime()` for each number.
5. Prints all prime numbers found.

## Complete Program Example: Sum of digits in a number

```gal
pollinate seed sumDigits(seed n) {
    seed sum = 0;
    seed digit;

    tend {
        digit = n % 10;
        sum = sum + digit;
        n = n / 10;
    } grow (n > 0);

    reclaim sum;
}

root() {
    seed number;
    seed result;

    plant("Enter a number: ");
    water(number);

    result = sumDigits(number);

    plant("Sum of digits: ");
    plant(result);
    plant("\n");

    reclaim;
}
```

This program:
1. Uses a `do-while` loop to extract each digit.
2. For example: 234 → 4 + 3 + 2 = 9.
3. Shows how to break a number into parts.

## Complete Program Example: 2D Array (Matrix)

```gal
root() {
    seed matrix[3][3];
    seed i;
    seed j;
    seed sum;

    // Fill the matrix
    cultivate (i = 0; i < 3; i++) {
        cultivate (j = 0; j < 3; j++) {
            matrix[i][j] = (i + 1) * (j + 1);
        }
    }

    // Print the matrix
    cultivate (i = 0; i < 3; i++) {
        cultivate (j = 0; j < 3; j++) {
            plant(matrix[i][j]);
            plant(" ");
        }
        plant("\n");
    }

    // Calculate sum of all elements
    sum = 0;
    cultivate (i = 0; i < 3; i++) {
        cultivate (j = 0; j < 3; j++) {
            sum = sum + matrix[i][j];
        }
    }

    plant("Total sum: ");
    plant(sum);
    plant("\n");

    reclaim;
}
```

This program:
1. Declares a 2D array (3x3 matrix).
2. Fills it with values using nested loops.
3. Prints the matrix by looping twice.
4. Sums all elements.

## Complete Program Example: Grade calculator

```gal
pollinate vine getGrade(seed score) {
    spring (score >= 90) {
        reclaim "A";
    } bud (score >= 80) {
        reclaim "B";
    } bud (score >= 70) {
        reclaim "C";
    } bud (score >= 60) {
        reclaim "D";
    } wither {
        reclaim "F";
    }
}

root() {
    seed score1;
    seed score2;
    seed score3;
    seed average;
    vine grade;

    plant("Enter 3 scores:\n");
    plant("Score 1: ");
    water(score1);
    plant("Score 2: ");
    water(score2);
    plant("Score 3: ");
    water(score3);

    average = (score1 + score2 + score3) / 3;
    grade = getGrade(average);

    plant("Average: ");
    plant(average);
    plant("\n");
    plant("Grade: ");
    plant(grade);
    plant("\n");

    reclaim;
}
```

This program calculates the grade based on average score using a separate function.

## Complete Program Example: Nested loops with conditions

```gal
root() {
    seed i;
    seed j;

    plant("Print grid with conditions:\n");

    cultivate (i = 1; i <= 5; i++) {
        cultivate (j = 1; j <= 5; j++) {
            spring ((i == j)) {
                plant("D ");  // Diagonal
            } bud ((i + j == 6)) {
                plant("A ");  // Anti-diagonal
            } wither {
                plant(". ");  // Rest
            }
        }
        plant("\n");
    }

    reclaim;
}
```

Output:
```
D . . . A 
. D . A . 
. . D . . 
. A . D . 
A . . . D 
```

Explanation:
- Nested loop creates a 5x5 grid.
- Prints "D" on the main diagonal (where `i == j`).
- Prints "A" on the anti-diagonal (where `i + j == 6`).
- Prints "." everywhere else.

## Quick reference: Key patterns in GAL

| Pattern | Syntax | Use Case |
|---------|--------|----------|
| **For loop** | `cultivate (seed i = start; i < limit; i++)` | Fixed number of iterations |
| **While loop** | `grow (condition)` | Unknown number of iterations |
| **Do-while loop** | `tend { ... } grow (condition);` | At least one iteration guaranteed |
| **If-else** | `spring (...) { } wither { }` | Binary decision |
| **If-else-if-else** | `spring (...) { } bud (...) { } wither { }` | Multiple conditions |
| **Switch** | `harvest (expr) { variety N: ... soil: ... }` | Multi-way branching |
| **Nested loops** | `cultivate (...) { cultivate (...) { } }` | Matrix/2D access |
| **Function call** | `result = functionName(args);` | Code reuse |
| **Array** | `seed arr[10];` | Store multiple values |
| **Struct** | `bundle Type { ... };` | Group related data |
| **Break (in loops)** | `prune;` | Exit loop early |
| **Continue (in loops)** | `skip;` | Skip to next iteration |

## Quick guide: when to use each data type

- Use `seed` when you need whole numbers.
- Use `tree` when you need decimals.
- Use `leaf` for a single character.
- Use `vine` for text.
- Use `branch` for true/false decisions.

This file is meant to serve as a comprehensive guide to GAL's reserved words, data types, control flow, functions, and real-world patterns. Use these examples as templates for writing your own GAL programs!
