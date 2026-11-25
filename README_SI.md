# Cartoon Studio Web App

Sinhala browser UI එකක් සහිත voice-to-cartoon MP4 generator එක.

## Local computer එකේ run කිරීම

අවශ්‍ය දේ:
- Python 3.10 හෝ ඉහළ
- FFmpeg සහ FFprobe install කර PATH එකට එක් කර තිබීම

Windows PowerShell / macOS / Linux terminal:

```bash
pip install -r requirements.txt
python app.py
```

ඉන්පසු browser එකෙන් `http://localhost:7860` විවෘත කරන්න.
Voice file එක upload කර title/script තෝරා `Cartoon MP4 හදන්න` ඔබන්න.

## Internet එකට deploy කිරීම

Dockerfile සහ `render.yaml` ඇතුළත් කර ඇත. GitHub repository එකකට මෙම folder එක push කර Render වැනි Docker hosting සේවාවකින් deploy කළ හැක.
Hosting provider එකේ persistent disk එකක් attach නොකළොත් server restart/deploy වලදී output files මැකී යා හැක.
Long renders සඳහා CPU/RAM සහ request time limits ප්‍රමාණවත් hosting plan එකක් අවශ්‍ය වේ.

## වැදගත්

- මෙය procedural 2D cartoon renderer එකකි; full 3D/AI image generation නොවේ.
- Script එක scene splitting සඳහා පමණි; audio speech recognition කරන්නේ නැත.
- Uploaded audio එක render අවසන් වූ පසු uploads folder එකෙන් ඉවත් කරයි.
- මෙය demo starter එකකි. Public production deployment එකකට authentication, rate limits, job cleanup, persistent storage, HTTPS සහ abuse protection එක් කරන්න.
- Default UI එකේ upload limit 100 MB. `MAX_UPLOAD_MB` environment variable එකෙන් වෙනස් කළ හැක.
