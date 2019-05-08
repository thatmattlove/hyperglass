| Expression               |                                                 Match |
| :----------------------- | ----------------------------------------------------: |
| `.\*`                    |                                              Anything |
| `.+`                     |                                         One Character |
| `^$`                     |                                          Local Routes |
| `\_65000$`               |                               Originated by `AS65000` |
| `^65000\_`               |                               Received from `AS65000` |
| `_65000_`                |                                         Via `AS65000` |
| `_65000_65001_`          |                           Via `AS65000` and `AS65001` |
| `_(65000_)+`             |                            Multiple `AS65000` in path |
| `^[0-9]+$`               |                                   AS_PATH length of 1 |
| `^[0-9]+_[0-9]+$`        |                                   AS_PATH length of 2 |
| `^[0-9]*_[0-9]+$`        |                              AS_PATH length of 1 or 2 |
| `^[0-9]*_[0-9]*$`        |                          AS_PATH length of 0, 1, or 2 |
| `^[0-9]+_[0-9]+_[0-9]+$` |                                   AS_PATH length of 3 |
| `_(65000\|65001)_`       | Anything that has gone through `AS65000` or `AS65001` |
| `_65000(_.+_)65001$`     | Anything from `AS65001` that passed through `AS65001` |
