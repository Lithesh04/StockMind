# Record the required 3-minute StockMind demonstration (Windows)

The repository contains the script and exact sequence, but not a pre-recorded video of your own laptop. Record the running application so the video proves that the software works on your system.

## Option A - Xbox Game Bar

1. Open StockMind in VS Code and start the Streamlit dashboard.
2. Open the local dashboard URL in Chrome or Edge.
3. Arrange the browser and, when needed, the VS Code terminal so the text is readable.
4. Press `Windows + G` to open Xbox Game Bar.
5. In the Capture panel, choose Record, or press `Windows + Alt + R` to start recording.
6. Follow `3_Minute_Presentation_Script.md` and show each dashboard tab.
7. Stop recording with `Windows + Alt + R`.
8. Find the recording in `Videos\Captures`.
9. Play it once to verify the audio/video, then upload it to the required submission location.

## Option B - OBS Studio

1. Install OBS Studio from its official website if your institution permits it.
2. Add a Display Capture or Window Capture source.
3. Add microphone audio only if you want to narrate.
4. Set recording output to MP4 or MKV (remux to MP4 if needed).
5. Record the 3-minute flow from the supplied script.
6. Check that terminal text and the dashboard are readable.

## Before you record

- Run `python main.py setup`.
- Run `python -m pytest -q` and confirm the tests pass.
- Start the Streamlit dashboard.
- Prepare the two-terminal socket demonstration if you plan to show it live.
- Run the live API tab only when internet access is working. If not, explain the network limitation and show the parser test; do not call sample fixture data a live result.
- Keep the private-key folder out of the recording and GitHub repository.
