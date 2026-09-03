# Changelog

All notable changes to ScreenInk. Newest first.

Version numbers that do not appear here were internal builds that were never published.

---

## 1.18.0 — 2026-09-02

**The setup wizard now looks like ScreenInk.**

- The installer showed generic stock artwork, which said nothing about what was being installed.
  It now carries the ScreenInk logo and name on its first and last pages, and a small mark in the
  banner across the pages in between.
- Nothing in the application itself changed. If you are already on 1.17.0 there is no reason to
  update, beyond seeing a nicer wizard the next time you do.

---

## 1.17.0 — 2026-09-02

**Activation keys are now checked properly.**

- ScreenInk re-checks its key once a day instead of once a fortnight, and it does so while it is
  running rather than only at startup. It lives in the tray on a machine that may go weeks between
  restarts, so "check at launch" was not a check at all.
- A failed check because the machine was offline is retried a couple of hours later, instead of
  waiting for the next launch.
- If a key has been withdrawn, ScreenInk says so and returns to Basic. Previously the Pro buttons
  would simply lock with no explanation.
- The sixty-day offline grace is unchanged, but when it does run out ScreenInk now tells you,
  rather than quietly changing behaviour.
- **Check now** on the About tab verifies the key as well as looking for a new build, and the About
  tab says plainly when the last confirmation is getting old.
## 1.16.0 — 2026-09-01

- The entry tier is now called **Basic** rather than Free, in the app and here. Nothing about what
  it includes has changed.

## 1.15.1 — 2026-09-01

- Said plainly that an activation key is not tied to a single machine. Deactivating a machine
  returns it to Basic; it does not "release" the key, because the key was never limited to one
  seat in the first place.

## 1.15.0 — 2026-08-31

**Automatic updates.**

- ScreenInk now checks for new builds itself — once a day, quietly, and only speaks up when there
  is something to install.
- **Settings ▸ About** shows the build you have, what is waiting, and installs it in place: it
  downloads the MSI, verifies it against the published SHA-256, shuts down cleanly, upgrades and
  restarts. Settings, custom shortcuts and activation all carry over.
- If an update fails, ScreenInk comes back on the build you already had and tells you what went
  wrong instead of leaving you with nothing.
- Upgrading no longer switches "Start with Windows" back on if you had turned it off.
- The daily check can be turned off.

**Pro activation.**

- Basic keeps the pen, highlighter, eraser and the full palette. A key adds shapes, typed captions,
  the spotlight and backdrops, region zoom, presentation cursors, fading ink, capture and custom
  keyboard shortcuts.
- Locked buttons stay on the toolbar with a small amber marker rather than vanishing, so it is
  always clear what a key would add.
- Activation needs the internet once, then works offline for months and re-confirms quietly every
  couple of weeks.

## 1.13.0 — 2026-08-31

- An unhandled error now writes `%APPDATA%\ScreenInk\crash.log` — stack, build and monitor layout —
  and shows a dialog that explains what happened, instead of disappearing silently.

## 1.12.0 — 2026-08-30

- The scroll wheel sizes a caption while the text tool is active, the same way it sizes a brush.
- A default text size in Settings ▸ Ink.

## 1.11.0 — 2026-08-30

- **Typed captions.** Click and type straight onto the screen. The caption stays live while you
  work on it — drag it to move it, click away to commit, <kbd>Esc</kbd> to cancel.
- Font family, bold and italic are configurable.

## 1.10.0 — 2026-08-30

- **Fading ink.** New marks dissolve on their own after Short, Medium, Long or Very long — scribble
  over a demo without ever stopping to clear the screen. <kbd>F</kbd> cycles the speed.
- **The scroll wheel sizes the brush**, live, while you draw.

## 1.9.0 — 2026-08-30

- A real mouse pointer is kept over ScreenInk's own toolbar and dialogs, so a presentation cursor
  no longer hides the button you are trying to click.
- The laser trail was rebuilt: a smooth tapered ribbon that fades from the back, instead of a line
  of separate dots.
- Added the **Soft Spotlight** presentation cursor.

## 1.8.0 — 2026-08-29

- Region capture now behaves like the Windows snipping overlay — the same frozen screen, the same
  dimmed surround and crosshair — and it appears instantly rather than fading in.

## 1.6.1 — 2026-08-26

- New application artwork.

## 1.6.0 — 2026-08-25

- Closing the toolbar leaves ScreenInk waiting in the notification area instead of quitting. Click
  the icon to bring the toolbar back; right-click ▸ Exit to quit for real.

## 1.5.1 — 2026-08-25

- The spotlight can be a 16:9 rectangle as well as a circle, and double-clicking it switches
  between the two.

## 1.5.0 — 2026-08-25

- Settings split into tabs, with an **Apply** button.
- Every keyboard shortcut is rebindable, with conflict detection.

## 1.4.1 — 2026-08-25

- First public build: layered overlay across every monitor, pen, highlighter, shapes, eraser, the
  colour palette, undo/redo/clear, dockable toolbar, global hotkeys, spotlight, backdrops, zoom,
  presentation cursors and capture.
