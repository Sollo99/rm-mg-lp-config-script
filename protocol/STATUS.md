# Protocol status

## Confirmed on the RM-MG-LP

### DPI

The Windows captures plus successful Linux tests establish:

```text
EP3[2][0] = DPI / 100
```

Observed/tested values:

```text
200   = 0x02
800   = 0x08
1200  = 0x0C
1600  = 0x10
16000 = 0xA0
```

### Polling

Observed control packets:

```text
125  -> 27 2B 85 FF 30 D5 76 76
250  -> 27 2B A5 FF D0 D5 76 76
500  -> 27 2B DD FF 00 1D 96 76
1000 -> 27 2B DD FF E8 25 96 76
```

The 500 Hz and 1000 Hz packets above are the verified values used by the utility. The `polling` command writes the selected packet directly as CTRL3. Although 125 Hz and 250 Hz packets were observed, the utility does not currently support setting those rates.

### RGB

The RGB capture showed changes confined to CTRL5 and CTRL6 during the RGB experiments.

Observed color packets, following the user's test order:

```text
green -> 27 2B 9D FF F0 F5 9D 6E
red   -> 27 2B 9D 04 98 F5 96 76
blue  -> 27 2B 9D FF F0 FA 2E 76
```

A captured standard-effect CTRL6 used with these states was:

```text
27 2B 6D FF E8 FD 9D 6E
```

### Buttons

EP3 #3 is an eight-slot table of 4-byte action descriptors.

Confirmed basic actions:

```text
left     -> 01 00 F0 00
right    -> 01 00 F1 00
middle   -> 01 00 F2 00
forward  -> 01 00 F4 00
backward -> 01 00 F3 00
```

Confirmed captured action descriptors:

```text
DPI cycle -> 07 00 03 00
DPI +     -> 07 00 01 00
DPI -     -> 07 00 02 00

poll cycle -> 05 00 03 00
poll +     -> 05 00 01 00
poll -     -> 05 00 02 00

double click -> 0A F0 32 02
triple click -> 0A F0 32 03
```

Linux button-write validation is still pending.

### Shortcuts

The UI supports modifier selection (Ctrl/Shift/Alt/Win) and an arbitrary keyboard key. The exact firmware encoding is not fully isolated yet.

### Macros

No macro was configured in the supplied capture, so macro encoding is not implemented.
