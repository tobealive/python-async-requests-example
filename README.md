# Python-async-requests-example

Example in python that focuses on concurrent async requests.

## Test runs

```
-------------------------------------------------------------------------------
1: Time: 6.91. Sent: 99. Successes: 98. Errors: 1. Timeouts: 0. Transferred: 24.52 MB (3.55 MB/s).
2: Time: 6.87. Sent: 99. Successes: 98. Errors: 1. Timeouts: 0. Transferred: 24.49 MB (3.56 MB/s).
3: Time: 6.95. Sent: 99. Successes: 98. Errors: 1. Timeouts: 0. Transferred: 24.47 MB (3.52 MB/s).
4: Time: 6.71. Sent: 99. Successes: 98. Errors: 1. Timeouts: 0. Transferred: 24.55 MB (3.66 MB/s).
5: Time: 6.76. Sent: 99. Successes: 98. Errors: 1. Timeouts: 0. Transferred: 24.37 MB (3.60 MB/s).
6: Time: 7.17. Sent: 99. Successes: 98. Errors: 1. Timeouts: 0. Transferred: 24.49 MB (3.42 MB/s).
7: Time: 6.66. Sent: 99. Successes: 98. Errors: 1. Timeouts: 0. Transferred: 24.55 MB (3.68 MB/s).
8: Time: 6.89. Sent: 99. Successes: 98. Errors: 1. Timeouts: 0. Transferred: 24.51 MB (3.56 MB/s).
9: Time: 6.82. Sent: 99. Successes: 98. Errors: 1. Timeouts: 0. Transferred: 24.42 MB (3.58 MB/s).
10: Time: 9.52. Sent: 99. Successes: 98. Errors: 1. Timeouts: 0. Transferred: 24.51 MB (2.58 MB/s).
-------------------------------------------------------------------------------
Runs: 10. Average Time: 7.13s. Total Errors: 10. Total Timeouts: 0. Transferred: 244.88 MB (3.44 MB/s).
-------------------------------------------------------------------------------
```

---

Single source requests (for simplicity `google.com/search?q=<1..100>`)

```
Time: 1.26s. Sent: 100. Successes: 100. Errors: 0. Timeouts: 0. Transferred: 0.62 MB (0.50 MB/s).
```

---

Supplementary information:

- The requests were sent from Germany

## Equivalents in other languages

- Nim: https://github.com/tobealive/nim-async-requests-example
- Haskell: https://github.com/tobealive/haskell-async-requests-example
