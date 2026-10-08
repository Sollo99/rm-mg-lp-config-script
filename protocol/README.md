# Protocol notes

These definitions are derived from RM-MG-LP captures and Linux tests.

The RM-MG-LP DPI encoding is:

```text
EP3[2][0] = DPI / 100
```

Do not substitute the older LUOM G10 `cpi // 50` encoding here.

The polling packets implemented by the utility are:

```text
500 Hz  -> 27 2B DD FF 00 1D 96 76
1000 Hz -> 27 2B DD FF E8 25 96 76
```

The `polling` command writes the selected packet directly as CTRL3. It supports 500 and 1000 Hz.
