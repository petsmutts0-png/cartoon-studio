# Android phone එකෙන් public website එකක් deploy කිරීම

මෙම project එක Docker web service එකක් ලෙස Render වෙත deploy කළ හැක.

## ඔබට අවශ්‍ය account
- GitHub account එකක් (source code repository සඳහා)
- Render account එකක් (hosting සඳහා)

## පියවර
1. ZIP එක Android phone එකට download කර Files app එකෙන් extract කරන්න.
2. GitHub හි නව repository එකක් සාදන්න: https://github.com/new
3. Repository එකේ files upload කර commit කරන්න. Repository එක private තබාගත හැක.
4. Render හි https://dashboard.render.com/ වෙත ගොස් GitHub account එක connect කරන්න.
5. **New → Web Service** තෝරා project repository එක තෝරන්න.
6. Runtime / Environment එක **Docker** ලෙස තෝරන්න. Root Directory හි project files තිබෙන folder එක root විය යුතුය.
7. Instance type එක Free තෝරා Create Web Service කරන්න.
8. Deploy සාර්ථක වූ පසු Render ලබාදෙන `https://....onrender.com` URL එක Android Chrome එකෙන් විවෘත කරන්න.

## Free hosting ගැන වැදගත් සීමා
- Render Free web service එක විනාඩි 15ක් traffic නැතිනම් sleep වෙනවා; නැවත open කරන විට wake වීමට මිනිත්තුවක් පමණ ගත විය හැක.
- Free instance එකේ local files persistent නොවේ. Restart / redeploy / sleep වීමෙන් upload සහ MP4 files නැතිවිය හැක. ඒ නිසා render ඉවර වූ වහාම MP4 එක download කරන්න.
- Free instance එකේ resource සීමා නිසා දිගු audio හෝ 1080p render අසාර්ථක විය හැක. මුලින් කෙටි voice clip එකක් සහ 720×1280 තෝරන්න.
- Public URL එකක් ඇති නිසා වෙනත් අයටත් website එකට පිවිසිය හැක. මෙම starter එකේ login, quota, rate-limit සහ private user storage තවම නැත. Public production භාවිතයට පෙර ඒවා එක් කළ යුතුය.
- දිගුකාලීන storage සහ විශ්වාසදායක rendering සඳහා paid hosting සහ persistent disk / object storage අවශ්‍ය විය හැක.
