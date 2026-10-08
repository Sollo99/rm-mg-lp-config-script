# This is just the beginning

I haven't had time to do more testing or reverse-engineer the Windows driver yet, but there's much more to come!

# Features

- Save and display the configuration managed by the utility.
- Change DPI from 200 to 16000 in 100-DPI steps.
- Change polling rate to 500 or 1000 Hz.
- Set static RGB colors and choose from 46 captured RGB presets.
- Preview changes with `--dry-run`.

# RM-MG-LP Linux Utility

Standalone user-space utility for the Rise Mode RM-MG-LP (`04d9:a09f`).

It does not depend on `luom-g10-config`. The devices appear to use a related controller/protocol family, but the configuration protocol I found for the RM-MG-LP is different from the one implemented there.

The project mentioned above was used as inspiration. :)

## Requirements

Python 3.10 or newer. Install the project and its dependencies from the project folder:

```bash
python3 -m pip install .
```

The commands below may need `sudo` if your user does not have permission to access the mouse.

## Commands

Show the configuration managed by the utility (saved locally; it is not read back from the mouse):

```bash
rm-mg-lpctl show
```

Show information about the connected mouse:

```bash
rm-mg-lpctl info
```

Change DPI:

```bash
rm-mg-lpctl dpi 1600
```

Change polling rate:

```bash
rm-mg-lpctl polling 500
rm-mg-lpctl polling 1000
```

Set static RGB colors:

```bash
rm-mg-lpctl rgb named green
rm-mg-lpctl rgb named red
rm-mg-lpctl rgb named blue
```

List available RGB presets and apply one of the 46 captured configurations:

```bash
rm-mg-lpctl list-rgb
rm-mg-lpctl rgb capture 2
```

## Dry run

Preview a change without sending anything to the mouse or saving the new state:

```bash
rm-mg-lpctl --dry-run dpi 1600
rm-mg-lpctl --dry-run polling 500
rm-mg-lpctl --dry-run rgb named green
```

DPI and RGB use the full configuration transaction. Polling uses the verified CTRL3 packet, so changing the polling rate does not rewrite the DPI or RGB configuration.

Button action packets can be printed for inspection, but writing button assignments to the mouse has not been validated on Linux. Shortcuts and macros are not implemented.

## Tested on the physical mouse

- DPI: 200–16000 in 100-DPI steps.
- Polling: 500 and 1000 Hz.
- Static RGB: red, green, and blue.

## State

The utility stores its configuration in:

```text
~/.config/rm-mg-lp/config.json
```

## Contact

If you have any questions or suggestions, you can contact me at:

`sollo9x@proton.me`
