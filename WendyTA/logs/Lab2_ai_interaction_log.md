## [2026-09-19 16:21:54] - Session Entry
**AI Assistant**: GitHub Copilot Chat (WendyTA)

### Code Changes
- **Files Modified**: `Lab 2/screen_clock.py`
- **AI-Generated Code**: Made the button-triggered dog photo display for two seconds before the comment appears.
- **Student Modifications**: Existing Lab 2 photo and comment implementation was preserved.

### Interaction Summary
- **Questions Asked**: Make the dog image and comment appear sequentially after a button press.
- **Answers Provided**: Added an explicit photo-only phase using a `comment_visible` state flag.
- **Learning Objectives**: Practice event timing and state transitions in a Raspberry Pi display loop.

### Next Steps
- Test the sequence on the Raspberry Pi and commit the interaction log with the code changes.

---

## [2026-09-19 17:49:04] - Session Entry
**AI Assistant**: GitHub Copilot Chat (WendyTA)

### Code Changes
- **Files Modified**: `Lab 2/screen_clock.py`
- **AI-Generated Code**: Reduced idle clock text to 12px, changed idle photo scaling to preserve the full image, expanded the photo area, and moved the moon cue lower.
- **Student Modifications**: Existing idle colors, right-column alignment, and shape-based cues were preserved.

### Interaction Summary
- **Questions Asked**: Show the complete idle dog image and move the lower dog/moon cue down one more icon height.
- **Answers Provided**: Replaced cropping with aspect-preserving thumbnail scaling, gave the image more vertical room, and moved the moon cue to `y=80`.
- **Learning Objectives**: Practice preserving image content and refining constrained display coordinates.

### Next Steps
- Test the complete idle dog image and lower cue position on the Raspberry Pi display.

---

## [2026-09-19 17:38:38] - Session Entry
**AI Assistant**: GitHub Copilot Chat (WendyTA)

### Code Changes
- **Files Modified**: `Lab 2/screen_clock.py`
- **AI-Generated Code**: Reduced idle clock text to 14px, moved the moon cue lower, and expanded the idle dog image upward while keeping its bottom edge visible.
- **Student Modifications**: Existing idle colors, icon shapes, and right-column alignment were preserved.

### Interaction Summary
- **Questions Asked**: Prevent the idle dog image from being cut off and separate the lower dog/moon cue from the upper cue.
- **Answers Provided**: Gave the image more vertical space and moved the moon cue down by approximately one icon height.
- **Learning Objectives**: Practice iterative coordinate adjustments for constrained hardware displays.

### Next Steps
- Test the revised idle screen on the Raspberry Pi display.

---

## [2026-09-19 17:32:28] - Session Entry
**AI Assistant**: GitHub Copilot Chat (WendyTA)

### Code Changes
- **Files Modified**: `Lab 2/screen_clock.py`
- **AI-Generated Code**: Moved the idle cues to the left, replaced photo icons with Pillow-drawn dog/sun/moon shapes, shifted clocks and idle photo right, and matched their widths.
- **Student Modifications**: Existing clock colors, idle dog asset, and event scenes were preserved.

### Interaction Summary
- **Questions Asked**: Correct idle cue placement, avoid unreliable emoji rendering, and align the right-side clock and image content.
- **Answers Provided**: Added reliable shape-based cues, reserved a left column, and switched idle clocks to hours and minutes.
- **Learning Objectives**: Practice display layout constraints, affordance placement, and raster drawing for hardware displays.

### Next Steps
- Test the left-side cues and right-column alignment on the Raspberry Pi display.

---

## [2026-09-19 17:12:48] - Session Entry
**AI Assistant**: GitHub Copilot Chat (WendyTA)

### Code Changes
- **Files Modified**: `Lab 2/screen_clock.py`
- **AI-Generated Code**: Enlarged the night welcome message and added running and sleeping dog image cues beside the upper and lower idle controls.
- **Student Modifications**: Existing event scenes, idle clock layout, and dog image assets were preserved.

### Interaction Summary
- **Questions Asked**: Make the welcome message larger than the greeting and show dog icons beside the default-screen button positions.
- **Answers Provided**: Increased the welcome font and rendered `dog_running.jpeg` above `dog_idle.jpg` on the idle screen.
- **Learning Objectives**: Practice visual hierarchy and using images as physical-control affordances.

### Next Steps
- Test the idle icon positions and enlarged night message on the Raspberry Pi display.

---

## [2026-09-19 16:57:53] - Session Entry
**AI Assistant**: GitHub Copilot Chat (WendyTA)

### Code Changes
- **Files Modified**: `Lab 2/screen_clock.py`
- **AI-Generated Code**: Configured the night event to use `dog_running.jpeg` as its photo.
- **Student Modifications**: The uploaded `dog_running.jpeg` file was preserved.

### Interaction Summary
- **Questions Asked**: Use `dog_running.jpeg` for the night photo.
- **Answers Provided**: Made the new image the preferred night-photo filename with existing fallbacks retained.
- **Learning Objectives**: Practice mapping a specific media asset to an event state.

### Next Steps
- Copy `dog_running.jpeg` beside `screen_clock.py` on the Raspberry Pi.

---

## [2026-09-19 16:55:33] - Session Entry
**AI Assistant**: GitHub Copilot Chat (WendyTA)

### Code Changes
- **Files Modified**: `Lab 2/screen_clock.py`
- **AI-Generated Code**: Changed the New York label to `NY`, reduced the idle clock font, and enlarged the idle dog image area.
- **Student Modifications**: Existing idle colors and time-zone behavior were preserved.

### Interaction Summary
- **Questions Asked**: Adjust the normal clock screen labels, text size, and dog image size.
- **Answers Provided**: Updated the idle layout dimensions and clock labels.
- **Learning Objectives**: Practice fitting text and images within a constrained display layout.

### Next Steps
- Test the idle screen on the Raspberry Pi display.

---

## [2026-09-19 16:52:07] - Session Entry
**AI Assistant**: GitHub Copilot Chat (WendyTA)

### Code Changes
- **Files Modified**: `Lab 2/screen_clock.py`
- **AI-Generated Code**: Added automatic return to the idle screen after five seconds, New York and Japan clock lines, and the `dog_idle.jpg` image below them.
- **Student Modifications**: Existing event scenes, button handling, colors, and uploaded image loading were preserved.

### Interaction Summary
- **Questions Asked**: Restore the clock after events, show two time zones, and add an idle dog image.
- **Answers Provided**: Added an event duration, timezone-aware clock rendering, and script-relative idle image loading.
- **Learning Objectives**: Practice timed state transitions, timezone-aware timestamps, and composing multiple display elements.

### Next Steps
- Copy `dog_idle.jpg` beside `screen_clock.py` on the Raspberry Pi and test the complete interaction.

---

## [2026-09-19 16:40:44] - Session Entry
**AI Assistant**: GitHub Copilot Chat (WendyTA)

### Code Changes
- **Files Modified**: `Lab 2/screen_clock.py`
- **AI-Generated Code**: Updated image loading to support `dog.jpg.JPG` and `dog_food.jpg.jpeg`, with paths resolved relative to the script.
- **Student Modifications**: Uploaded image files were preserved.

### Interaction Summary
- **Questions Asked**: Uploaded images were not loading on the Raspberry Pi.
- **Answers Provided**: Identified the filename and case mismatch, then added compatible filename handling.
- **Learning Objectives**: Understand case-sensitive filenames, file extensions, and script-relative paths.

### Next Steps
- Copy both image files beside `screen_clock.py` on the Raspberry Pi and run the script from there.

---

## [2026-09-19 16:36:49] - Session Entry
**AI Assistant**: GitHub Copilot Chat (WendyTA)

### Code Changes
- **Files Modified**: `Lab 2/screen_clock.py`
- **AI-Generated Code**: Enlarged the Japan photo caption, removed `FOOD!`, and restyled the night scene with a navy background, white text, and visible strikethroughs.
- **Student Modifications**: Existing scene timing and button behavior was preserved.

### Interaction Summary
- **Questions Asked**: Correct the morning text, improve caption readability, and fix the night scene styling and strike line.
- **Answers Provided**: Added dedicated caption and welcome fonts, removed the unwanted label, and explicitly drew the night strike lines.
- **Learning Objectives**: Practice readable typography, scene-specific styling, and explicit drawing order.

### Next Steps
- Test the updated visuals on the Raspberry Pi display.

---

## [2026-09-19 16:28:13] - Session Entry
**AI Assistant**: GitHub Copilot Chat (WendyTA)

### Code Changes
- **Files Modified**: `Lab 2/screen_clock.py`
- **AI-Generated Code**: Replaced the side-by-side event layout with a one-second full-screen photo scene followed by a full-screen comic message, and added independent button press detection.
- **Student Modifications**: Existing button and photo setup was preserved.

### Interaction Summary
- **Questions Asked**: Separate the two visual scenes and fix the second button not triggering the night version.
- **Answers Provided**: Added timed scene renderers and button edge detection so either button can start a new event.
- **Learning Objectives**: Practice full-screen composition, timed state transitions, and handling active-low button press edges.

### Next Steps
- Test both buttons on the Raspberry Pi, releasing each button between presses.

---