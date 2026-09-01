# ScreenInk — downloads

Draw over anything on screen while you present: pen, highlighter, shapes, captions, spotlight and
zoom, on a layered overlay that spans every monitor and lets your slides keep the keyboard focus.

**[Download the latest release](https://github.com/alexusa75/ScreenInk-releases/releases/latest)**

Windows 11 and Windows 10. The installer is per-user, so it needs no administrator prompt, and the
application is self-contained — nothing else has to be installed first.

This repository holds the installers and the update feed only. It exists so that ScreenInk can
check for and install its own updates without asking anyone for a credential.

---

## Installing

Download `ScreenInk-<version>-x64.msi` from the latest release and run it. To install without any
prompts:

```powershell
msiexec /i ScreenInk-1.13.0-x64.msi /qn
```

Your settings live in `%APPDATA%\ScreenInk` and survive upgrades and removals.

## Updating

ScreenInk checks quietly for new builds and offers to install them for you: it downloads the
installer, verifies it against the checksum published here, replaces itself and restarts. Settings
are kept. You can turn the check off, or run it on demand, in **Settings ▸ General**.

## Removing it

Settings ▸ Apps ▸ ScreenInk ▸ Uninstall. If Windows Installer refuses — some machines fail on their
own rollback folder with `Could not set file security ... Error: 5` — use
[`Remove-ScreenInk.ps1`](https://github.com/alexusa75/ScreenInk-releases/releases/latest) from the
release assets, which gets past it and cleans up by hand.

---

## Pro

ScreenInk is free to install and free to use for annotating a screen. An activation key unlocks the
rest.

| | Free | Pro |
|---|:---:|:---:|
| Pen, highlighter, eraser | ● | ● |
| Full colour palette and stroke widths | ● | ● |
| Undo, redo, clear | ● | ● |
| Draw across every monitor | ● | ● |
| Dockable toolbar and global hotkeys | ● | ● |
| Lines, arrows, rectangles, ellipses | | ● |
| Typed captions | | ● |
| Spotlight, and white, black and dimmed backdrops | | ● |
| Zoom | | ● |
| Presentation cursors and the laser trail | | ● |
| Fading ink | | ● |
| Save and copy the screen or a region | | ● |
| Custom keyboard shortcuts | | ● |

Enter a key in **Settings ▸ Licence**. Activation needs the internet once; after that ScreenInk
works offline, and re-checks quietly every couple of weeks. A key can be moved between machines —
deactivate it on the old one first.

`keys.json` in this repository records the SHA-256 of every key issued. A hash cannot be turned
back into a key, so publishing it gives away nothing; it is what lets ScreenInk confirm a key is
genuine, and what lets a lost or misused key be withdrawn.

---

## Reporting a problem

If ScreenInk closes with an error it writes `%APPDATA%\ScreenInk\crash.log`, with the stack, the
build and the monitor layout at the time. Attach it to an issue here — that file is usually the
difference between a fix and a guess.
